from matplotlib.backend_bases import NavigationToolbar2
import networkx as nx
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Graph import CustomGraph
import time
from best_first_search import Variants


class Animation:
    def __init__(self, algorithm):
        self.problem = algorithm
        self.graph = algorithm.problem
        self.frame_number = 0
        self.animate = None
        self.direction = 1  # 1 stands for forward
        self.is_rendered = True  # to make sure that the backward frame is rendered
        self.is_start = True

    def get_parent_path(self, path):

        current_node = path[-1]
        parent_path = [current_node]

        while current_node.parent is not None:
            parent_path.append(current_node.parent)
            current_node = current_node.parent

        return [[node.parent.state if node.parent is not None else node.state,
                 node.state] for node in parent_path]

    def get_beam_parent_paths(self, path, depth):
        nodes = self.get_nodes_withs_same_depth(path, depth)

        result = []
        for current_node in nodes:
            parent_path = [current_node]
            while current_node.parent is not None:
                parent_path.append(current_node.parent)
                current_node = current_node.parent
                result.extend([[node.parent.state if node.parent is not None else node.state,
                                node.state] for node in parent_path]
                              )

        return result

    def get_ordered_nodes(self, path):
        current_node = path[-1]
        parent_path = [current_node.state]

        while current_node.parent is not None:
            parent_path.append(current_node.parent.state)
            current_node = current_node.parent
        return parent_path

    def get_path_history(self):

        path = self.problem.search()
        path_history = []
        if (self.problem.algorithm != Variants.BEAM):
            # Generate animation frames
            if path is not None:
                for i in range(len(path)):
                    partial_path = path[:i+1]

                    path_history.append(partial_path)

        else:
            # for beam search the history is generated based on the depht of nodes
            # the max depth if the one of the last node in the path returned from the algorithm
            for i in range(path[-1].depth+1):
                partial_path = self.get_nodes_withs_same_depth(path, i)
                path_history.append(partial_path)
        return path_history

    def get_nodes_withs_same_depth(self, nodes, depth):
        result = []
        for node in nodes:
            if node.depth == depth:
                result.append(node)
        return result

    def node_colors(self, path, unpacked_parent_path, depth=0):
        if (self.problem.algorithm != Variants.BEAM):
            return ['orange' if node == self.problem.initial_node else 'green' if node.state in self.problem.goal_states else 'yellow'
                    if node.state in self.problem.goal_states
                    else 'violet' if node == path[-1] else 'green'
                    if (path[-1].state in self.problem.goal_states and node.state in unpacked_parent_path)else
                    'blue' if node.state in unpacked_parent_path else 'red' for node in path]
        else:
            current_nodes = self.get_nodes_withs_same_depth(path, depth)
            return ['orange' if node == self.problem.initial_node else 'violet' if node in current_nodes else 'green' if (node.state in self.problem.goal_states )else 'blue' if node.state in unpacked_parent_path else 'red' for node in path]

    def set_title(self, ax, cost, path):
        title = ""
        if (self.problem.algorithm == Variants.GREEDY):
            title += "GREEDY"
        elif (self.problem.algorithm == Variants.UCS):
            title += "UCS"
        elif (self.problem.algorithm == Variants.A_star):
            title += "A Star"
        elif (self.problem.algorithm == Variants.DFS):
            title += "DFS"
        elif (self.problem.algorithm == Variants.DPL):
            title += "DPL with Max depth : " + str(self.problem.limit)
        elif (self.problem.algorithm == Variants.BFS):
            title += "BFS"
        elif (self.problem.algorithm == Variants.BEAM):
            title += "BEAM" + " with width: " + str(self.problem.beam_width)
        elif (self.problem.algorithm == Variants.IDS):
            title += "Iterative deepening Search" + \
                " with max depth: " + \
                str(self.problem.max_depth) + \
                " and step of : "+str(self.problem.step)

        title += "\n"
        if (self.problem.algorithm != Variants.BEAM):
            title += f"->".join(self.get_ordered_nodes(path)[::-1])
            title += "\n"
        title += f"path cost: {cost}"

        ax.set_title(title, fontsize=20)

    def set_legend(self, ax):
        color_dict = {'visited before': 'red', 'current node': 'violet',
                      'visited now ': 'blue',
                      'goal node': 'green', 'initial node': 'orange', 'not visited': 'black'}

        legend_patches = [mpatches.Patch(
            color=color, label=label) for label, color in color_dict.items()]

        ax.legend(handles=legend_patches)

    def update(self, num, path_history, ax, G, pos):

        graph_dict = self.graph.graph_dict

        # if (not self.is_start):
        #  # Get the current path
        #    if (self.direction == 1):
        #        self.frame_number += 1
        #        self.frame_number %= len(path_history)
        #    else:
        #        self.frame_number -= 1
        #        if (self.frame_number == -1):
        #            self.frame_number = 0
#
        # else:
        #    self.is_start = False
        path = path_history[num]
        ax.clear()
        #self.frame_number = num

        # drawing the base edges
        nx.draw_networkx_edges(G, pos=pos, edgelist=G.edges(),
                               ax=ax, edge_color="gray", width=6, alpha=0.5)

        # Background nodes and edges(That is the nodes and edges that are not visited yet)
        null_nodes = nx.draw_networkx_nodes(
            G, pos=pos, nodelist=set(G.nodes())-set(self.problem.goal_states), node_color="black", ax=ax, node_size=1200)
        nx.draw_networkx_nodes(
            G, pos=pos, nodelist=set(self.problem.goal_states), node_color="green", ax=ax, node_size=1200)

        node_labels = CustomGraph.get_node_labeles_heuristic(
            problem=graph_dict)
        nx.draw_networkx_labels(G, pos=pos, labels=dict(zip(graph_dict.keys(), node_labels)),
                                font_color="white", ax=ax, font_size=10, font_family="sans-serif")
        null_nodes.set_edgecolor("black")

        # get the parent path so tha we can color the edges and nodes that are visited,not visted and the currently visited node
        parent_path = self.get_parent_path(path)
        unpacked_parent_path = [
            element for trace in parent_path for element in trace]

        query_nodes = nx.draw_networkx_nodes(
            G, pos=pos, nodelist=[node.state for node in path], node_color=self.node_colors(path, unpacked_parent_path, depth=num),
            ax=ax, node_size=1200)
        query_nodes.set_edgecolor("white")

        edgelist = [[node.parent.state if node.parent is not None else node.state,
                     node.state] for node in path]

        # color any other path not from the parent node wtih the red color
        if (self.problem.algorithm != Variants.BEAM):
            nx.draw_networkx_edges(G, pos=pos, edgelist=[v for v in edgelist if v not in parent_path],
                                   edge_color="red", ax=ax, width=6, alpha=0.5)

            nx.draw_networkx_edges(G, pos=pos, edgelist=parent_path, width=6, alpha=0.5,
                                   edge_color=["green" if path[-1].state in self.problem.goal_states else "blue"], ax=ax)
        else:
            beam_parent_path = self.get_beam_parent_paths(path, num)
            nx.draw_networkx_edges(G, pos=pos, edgelist=beam_parent_path, width=6, alpha=0.5,
                                   edge_color=["green" if path[-1].state in self.problem.goal_states else "blue"], ax=ax)

        # drawing the costs
        edge_labels = nx.get_edge_attributes(G, "weight")
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels, font_size=10, font_family="sans-serif")

        self.set_title(ax, path[-1].cost, path)
        self.set_legend(ax)
        # if (self.direction == 0):
        #    if (self.is_rendered == False):
        #        self.is_rendered = True
        #        self.direction = 1

    def backward(self):
        self.is_rendered = False
        self.direction = 0

    def animation_pop_up(self):
        G = self.graph.get_nx_graph()
        # print(G.nodes())
        pos = nx.spring_layout(G)

        fig, ax = plt.subplots(figsize=(20, 20))
        # perform the Search algorithm
        path_history = self.get_path_history()
        print(path_history)

        # creating the Tkinter Window
        root = tk.Tk()

        def kill():
            root.destroy()
            root.quit()
        root.geometry("1920x1080")
        canvas = tk.Canvas(root)
        canvas.pack()
        self.animate = animation.FuncAnimation(fig, self.update, frames=len(
            path_history), fargs=(path_history, ax, G, pos), interval=3000, repeat=True)
        pause_button = tk.Button(
            canvas, text="Pause Animation", command=self.animate.pause)
        pause_button.pack()

        resume_button = pause_button = tk.Button(
            canvas, text="Resume Animation", command=self.animate.resume)

        backward_button = pause_button = tk.Button(
            canvas, text=" Backward", command=self.backward)
        # backward_button.pack()

        resume_button.pack()

        # Create a Matplotlib figure and attach it to the canvas
        fig_agg = FigureCanvasTkAgg(fig, master=canvas)
        fig_agg.get_tk_widget().pack()
        root.protocol("WM_DELETE_WINDOW", kill)
        root.mainloop()

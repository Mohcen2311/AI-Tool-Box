import networkx as nx


class CustomGraph:
    def __init__(self, graph):
        if (isinstance(graph, dict)):
            self.graph_dict = graph
            self.graph_nx = self.__create_nx_graph(graph)

    def get_graph_dict(self):
        return self.graph_dict

    def get_nx_graph(self):
        return self.graph_nx

    def __create_nx_graph(self, graph):
        G = nx.Graph()
        G.add_nodes_from(graph.keys())
        for k, v in graph.items():
            G.add_edges_from([(k, t[0], {
                "weight": t[1]}) for t in v if not isinstance(t, int)])
        return G

    def add_edge(self, node_a_state, node_b_state, weight):
        pass

    def add_node(self, state, heuristic):
        pass

    @staticmethod
    def get_node_labeles_heuristic(problem):
        node_lables = []
        for k, v in problem.items():
            h = CustomGraph.min_heuristic_value(v)
            node_lables.append(f"{k}\n h={h}")
        return node_lables

    @staticmethod
    def min_heuristic_value(value):
        min_value = float("inf")
        for v in value:
            if isinstance(v, int):
                min_value = min(min_value, v)
        return min_value

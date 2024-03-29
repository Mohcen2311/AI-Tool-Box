class Node:

    """
    state:is the state object 
    cost:is the real cost of the node starting from the initial state state 
    score:is the  score of the node depending on the algorithm
    parent:is the parent node 
    action:action taken from parent to reach that node(from the set of legal actions)
    depth:The depth of the node (Used for iterative depening search)
    """

    def __init__(self, state, cost, score, parent, action, depth=None):
        self.state = state
        self.cost = cost
        self.score = score
        self.parent = parent
        self.action = action
        self.depth = depth

    def __str__(self):
        return self.state

    def __lt__(self, other):

        return self.score < other.score

    def __eq__(self, other):
        print(self, other)
        return self.state == other.state

    def __hash__(self):
        return hash(self.state)
    
    def __repr__(self) -> str:
        return f"{self.state}, {self.parent}"

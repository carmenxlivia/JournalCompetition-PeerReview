import networkx as nx
import Model.systemMetrics as sm


class SocialNetwork:
    """Class for representing the social network"""

    def __init__(self, no_agents):
        self.noNodes = no_agents
        self.maxSocialDist = 0
        self.minSocialDist = no_agents
        self.graph = nx.Graph()
        self.shortestPathMatrix = dict(nx.all_pairs_shortest_path_length(self.graph))

    def createSocialNetwork(self):

        if sm.social_network_type == 1:
            # RING NETWORK
            for i in range(self.noNodes - 1):
                self.graph.add_edge(i, i + 1)
            self.graph.add_edge(0, self.noNodes - 1)
        elif sm.social_network_type == 2:
            # SMALL WORLD NETWORK
            self.graph = nx.watts_strogatz_graph(self.noNodes, 5, 0.5)
        else:
            # RANDOM NETWORK
            self.graph = nx.erdos_renyi_graph(self.noNodes, 0.1)


        self.createShortestPathMatrix()

        # calculate maximum social distance existing in the network
        social_max = 0
        for node in range(0, self.noNodes):
            current_max = max(self.shortestPathMatrix[node].values())
            social_max = (current_max > social_max and current_max or social_max)
        self.maxSocialDist = social_max

        # calculate minimum social distance existing in the network
        social_min = self.noNodes
        for node in range(0, self.noNodes):
            # delete the node lengths to themselves ( 0 lengths )
            shortest_path_list = list(self.shortestPathMatrix[node].values())
            shortest_path_list = list(filter(lambda a: a != 0, shortest_path_list))
            current_min = min(shortest_path_list)
            social_min = (current_min < social_min and current_min or social_min)
        self.minSocialDist = social_min

    def getShortestPathBetweenNodes(self, source, target):
        return self.shortestPathMatrix[source].get(target)

    def createShortestPathMatrix(self):
        self.shortestPathMatrix = dict(nx.all_pairs_shortest_path_length(self.graph))

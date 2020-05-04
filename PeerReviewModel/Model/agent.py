from Model.reviewStrategy import ReviewStrategy
from random import choice, uniform, choices
import Model.systemMetrics as sm


def computeSocialDistanceEffect(sd):
    if sm.maxSocialDist == sm.minSocialDist:
        return 0.5
    else:
        return (sm.maxSocialDist - sd) / (sm.maxSocialDist - sm.minSocialDist)


def computeReputationEffect(author_reputation):
    if sm.maxReputation == sm.minReputation:
        return 0.5
    return 1 - ((sm.maxReputation - author_reputation) / (sm.maxReputation - sm.minReputation))


class Agent:
    """Class for representing the agent"""
    def __init__(self, unique_id):

        self.unique_id = unique_id

        if sm.fix_agents:
            self.manuscriptStrategy = 0.99115
            self.reviewStrategy = ReviewStrategy(1, 1, 0.9294, 0.073, -0.858, -0.9705, 0.9481, 0.15894, 0.6941, -0.8368)
        else:
            self.manuscriptStrategy = uniform(0, 1)
            self.reviewStrategy = ReviewStrategy(choice([0, 1]), choice([0, 1]), uniform(0, 1), uniform(0, 1),
                                                 uniform(-1, 1), uniform(-1, 1), uniform(0, 1), uniform(0, 1),
                                                 uniform(-1, 1), uniform(-1, 1))

        self.topicPos = uniform(0, 2)
        self.publicReputation = 0
        self.payoff = 0
        self.manuscriptList = [{} for i in range(sm.time)]
        self.reviewlist = [[] for i in range(sm.time)]

    def printAttributes(self):
        print("*** AGENT no.  ", self.unique_id, " ***")
        print("Manuscript strategy is: ", self.manuscriptStrategy)
        print("Topic Pos is: ", self.topicPos)
        self.reviewStrategy.printReviewStrategy()

    def createPaper(self):
        population = [1, 0]
        weights = [self.manuscriptStrategy, 1 - self.manuscriptStrategy]
        return choices(population, weights)[0]

    def computeTopicDistanceEffect(self, author_topic_pos):
        self_topic_pos = self.topicPos
        result1 = max(author_topic_pos, self_topic_pos) - min(author_topic_pos, self_topic_pos)
        result2 = 2 - result1
        return min(result1, result2)

    def computeConditionalProbability(self, type_cond, sd, author):
        # conditional review
        if type_cond == 1:
            w_social_dist = self.reviewStrategy.wQsd
            w_topic_dist = self.reviewStrategy.wQtd
            w_reputation = self.reviewStrategy.wQrep
        else:
            # conditional acceptance
            w_social_dist = self.reviewStrategy.wAsd
            w_topic_dist = self.reviewStrategy.wAtd
            w_reputation = self.reviewStrategy.wArep

        social_distance_effect = computeSocialDistanceEffect(sd)
        topic_distance_effect = self.computeTopicDistanceEffect(author.topicPos)
        reputation_effect = computeReputationEffect(author.publicReputation)

        minElem = min([w_social_dist, w_topic_dist, w_reputation])
        denominator = (w_social_dist + w_topic_dist + w_reputation - 3 * minElem + 3)
        numerator = (social_distance_effect * (w_social_dist - minElem + 1) + topic_distance_effect * (
                w_topic_dist - minElem + 1) + reputation_effect * (w_reputation - minElem + 1))

        return numerator / denominator

    def computeAcceptance(self, author, sd):
        if self.reviewStrategy.propA == 1:
            pa = self.reviewStrategy.pa
        else:
            pa = self.computeConditionalProbability(2, sd, author)
        return choices([1, 0], [pa, 1 - pa])[0]

    def computeReview(self, author, sd):
        if self.reviewStrategy.propQ == 1:
            ph = self.reviewStrategy.ph
        else:
            ph = self.computeConditionalProbability(1, sd, author)
        return choices([1, 0], [ph, 1 - ph])[0]

    def reviewPaper(self, paper, author, sd):
        review_result = self.computeReview(author, sd)
        if review_result == 1:
            return paper
        else:
            return self.computeAcceptance(author, sd)

    def updateManuscriptList(self, paper, journal, accepted, time):
        self.manuscriptList[time] = {
            "journal": journal,
            "trueQuality": paper,
            "accepted": accepted
        }

    def updateReviewList(self, paper, journal, review, time):
        self.reviewlist[time].append({
            "journal": journal,
            "trueQuality": paper,
            "reviewQuality": review
        }
        )

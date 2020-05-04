from random import choice
import Model.systemMetrics as sm
from random import randint, uniform


class Journal:
    """Class for representing the journal"""
    def __init__(self, unique_id):
        self.unique_id = unique_id

        if sm.fix_journals:
            self.disagreementStrategy = 1
            self.maxPapers = 20
            self.allowableSocialDist = 2
            self.allowableTopicDist = 0.5
        else:
            self.disagreementStrategy = randint(1, 4)
            self.maxPapers = randint(sm.no_journals / 2, sm.no_journals + (sm.no_journals / 2))
            self.allowableSocialDist = randint(1, sm.no_agents / 2)
            self.allowableTopicDist = uniform(0, 1)

        self.goodPapers = 0
        self.badPapers = 0

        self.acceptanceRate = 0
        self.jif = 0

        self.noSubmissions = 0
        self.noAcceptedPapers = 0
        self.currentPapersAccepted = []

        self.jifList = [1] * sm.time

    def printAttributes(self):
        print("*** Journal no ", self.unique_id, " ***")
        print("Disagreement strategy: ", self.disagreementStrategy, " Max # papers ", self.maxPapers)
        print("Allowable social distance: ", self.allowableSocialDist, " allowable topic distance ",
              self.allowableTopicDist)
        print("JIF: ", self.jif)

    def solveDisagreement(self, reviewers, review_result):
        switcher = {
            1: 1,
            2: choice(review_result),
            3: (reviewers[0].publicReputation > reviewers[1].publicReputation and review_result[0] or review_result[1]),
            4: 0
        }
        return switcher.get(self.disagreementStrategy)

    def calculateAcceptanceRate(self):
        self.acceptanceRate = 0
        if self.noSubmissions != 0:
            self.acceptanceRate = self.noAcceptedPapers / self.noSubmissions

    def calculateJif(self, time):
        self.jif = 0
        gp = 0
        bp = 0
        for paper in self.currentPapersAccepted:
            if paper['quality'] == 1:
                gp += 1
            else:
                bp += 1
        self.badPapers += bp
        self.goodPapers += gp

        if self.goodPapers + self.badPapers != 0:
            self.jif = sm.alpha_jif * (self.goodPapers / (self.goodPapers + self.badPapers))
        self.jifList[time] = self.jif

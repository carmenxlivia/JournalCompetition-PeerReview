from random import choices, choice, sample
from random import uniform

import Model.systemMetrics as sm
from Model.agent import Agent
from Model.journal import Journal
from Model.socialNetwork import SocialNetwork


class PeerReviewModel:
    """Class which consists of the main code for our model"""

    def __init__(self, no_agents, no_journals):
        self.no_agents = no_agents
        self.no_journals = no_journals
        self.agentList = [Agent(i) for i in range(self.no_agents)]
        self.journalList = [Journal(i) for i in range(self.no_journals)]
        self.socialNetwork = SocialNetwork(self.no_agents)
        self.socialNetwork.createSocialNetwork()

    def printJournalList(self):
        for elem in self.journalList:
            elem.printAttributes()

    def printAgentList(self):
        for elem in self.agentList:
            elem.printAttributes()

    def printSocialNetwork(self):
        print(list(self.socialNetwork.graph.edges))

    def calculateMaxReputation(self):
        max_reputation = -1
        for agent in self.agentList:
            reputation = agent.publicReputation
            max_reputation = reputation if reputation > max_reputation else max_reputation
        return max_reputation

    def calculateMinReputation(self):
        min_reputation = 100
        for agent in self.agentList:
            reputation = agent.publicReputation
            min_reputation = reputation if reputation < min_reputation else min_reputation
        return min_reputation

    def calculateOverallJif(self):
        total_jif = 0
        for journal in self.journalList:
            total_jif += journal.jif
        return total_jif

    def calculateJournalsProb(self):
        weights = [0] * self.no_journals
        total_jif = self.calculateOverallJif()
        for journal in self.journalList:
            if total_jif == 0:
                weights[journal.unique_id] = 1
            else:
                weights[journal.unique_id] = journal.jif / total_jif
        return weights

    def submitPaper(self, time):
        if time > 10:
            chosen_journal = choices(population=self.journalList, weights=self.calculateJournalsProb(), k=1)[0]
        else:
            chosen_journal = choice(self.journalList)
        return chosen_journal

    def computePotentialReviewersUsingSocialDist(self, author, min_social_dist_allowed):
        list_allowable_reviewers = []
        for reviewer in self.agentList:
            if reviewer.unique_id != author:
                path_length = self.socialNetwork.getShortestPathBetweenNodes(reviewer.unique_id, author)
                if path_length >= min_social_dist_allowed:
                    list_allowable_reviewers.append(reviewer)
        return list_allowable_reviewers

    def computePotentialReviewersUsingTopicDistance(self, author, max_topic_distance_allowed):
        list_allowable_reviewers = []
        author_topic_pos = self.agentList[author].topicPos
        for reviewer in self.agentList:
            if reviewer.unique_id != author:
                reviewer_topic_pos = reviewer.topicPos
                topic_dist = min(
                    (max(author_topic_pos, reviewer_topic_pos) - min(author_topic_pos, reviewer_topic_pos)),
                    2 - (max(author_topic_pos, reviewer_topic_pos) - min(author_topic_pos, reviewer_topic_pos)))
                if max_topic_distance_allowed >= topic_dist:
                    list_allowable_reviewers.append(reviewer)
        return list_allowable_reviewers

    def getPotentialReviewers(self, author, journal):
        list_reviewers_social_dist = self.computePotentialReviewersUsingSocialDist(author, journal.allowableSocialDist)
        list_reviewers_topic_dist = self.computePotentialReviewersUsingTopicDistance(author, journal.allowableTopicDist)
        list_potential_reviewers = set(list_reviewers_social_dist) & set(list_reviewers_topic_dist)

        no_reviewers = 2

        if len(list_potential_reviewers) < no_reviewers:
            print("Found ", len(list_potential_reviewers), " rather than at least ", no_reviewers,
                  "reviewers for the paper written by author ", author)
            if len(list_reviewers_social_dist) >= no_reviewers:
                return sample(list_reviewers_social_dist, no_reviewers)
            else:
                if len(list_reviewers_topic_dist) >= no_reviewers:
                    return sample(list_reviewers_topic_dist, no_reviewers)
            return []
        reviewer_list = sample(list_potential_reviewers, no_reviewers)
        return reviewer_list

    def computeEditorialReputation(self, agent_id, journal, time):
        agent = self.agentList[agent_id]
        gpTimesJif = 0
        rej = 0
        bp = 0
        tau = (time > sm.time_window) and (time - sm.time_window) or 0
        gr = 0
        br = 0
        for i in range(tau, time + 1):
            paper = agent.manuscriptList[i]
            if paper != {}:
                if paper.get("trueQuality") & paper.get("accepted"):
                    journal_accepted = paper.get("journal")
                    gpTimesJif += self.journalList[journal_accepted].jifList[time]
                if paper.get("accepted") == 0 and paper.get("journal") == journal:
                    rej += 1
                if paper.get("accepted") == 1 and paper.get("trueQuality") == 0:
                    bp += 1
                reviews_curr_time = agent.reviewlist[i]
                for review in reviews_curr_time:
                    if review.get("journal") == journal:
                        if review.get("trueQuality") == review.get("reviewQuality"):
                            gr += 1
                        else:
                            br += 1

        return gpTimesJif - rej - sm.alpha_reputation * bp + sm.gamma * (gr - br)

    def step(self, time):
        """Code corresponding for the actions performed each time step by the agents and journals """

        # manuscript creation and reviewing task are performed by agents
        for agent in self.agentList:
            paper = agent.createPaper()
            chosen_journal = self.submitPaper(time)
            chosen_journal.noSubmissions += 1
            reviewers = self.getPotentialReviewers(agent.unique_id, chosen_journal)

            if len(reviewers) > 1:
                sd0 = self.socialNetwork.getShortestPathBetweenNodes(agent.unique_id, reviewers[0].unique_id)
                sd1 = self.socialNetwork.getShortestPathBetweenNodes(agent.unique_id, reviewers[1].unique_id)
                result0 = reviewers[0].reviewPaper(paper, agent, sd0)
                result1 = reviewers[1].reviewPaper(paper, agent, sd1)
                paper_accepted = result0 & result1

                if result0 != result1:
                    paper_accepted = chosen_journal.solveDisagreement(reviewers, [result0, result1])
                if paper_accepted:
                    chosen_journal.currentPapersAccepted.append(
                        dict({'author': agent.unique_id, 'reputation': agent.publicReputation, 'quality': paper}))

                agent.updateManuscriptList(paper, chosen_journal.unique_id, paper_accepted, time)
                reviewers[0].updateReviewList(paper, chosen_journal.unique_id, result0, time)
                reviewers[1].updateReviewList(paper, chosen_journal.unique_id, result1, time)

        # JIF calculation and selection of papers to be published - for each journal
        for journal in self.journalList:
            journal.noAcceptedPapers = len(journal.currentPapersAccepted)
            if journal.noAcceptedPapers > journal.maxPapers:
                for submission in journal.currentPapersAccepted:
                    author = submission['author']
                    current_journal = journal.unique_id
                    editorial_reputation = self.computeEditorialReputation(author, current_journal, time)
                    submission['reputation'] = editorial_reputation
                journal.currentPapersAccepted = sorted(journal.currentPapersAccepted, key=lambda k: k['reputation'],
                                                       reverse=True)
                declined_papers = journal.currentPapersAccepted[journal.maxPapers:]
                journal.currentPapersAccepted = journal.currentPapersAccepted[:journal.maxPapers]
                journal.noAcceptedPapers = len(journal.currentPapersAccepted[:journal.maxPapers])
                for paper in declined_papers:
                    self.agentList[paper['author']].manuscriptList[time]['accepted'] = 0
            journal.calculateJif(time)
            journal.calculateAcceptanceRate()
            journal.noSubmissions = 0
            journal.noAcceptedPapers = 0
            journal.currentPapersAccepted = []

        # PAYOFF and REPUTATION for each agent are updated
        tau = (time > sm.time_window) and (time - sm.time_window) or 0
        for agent in self.agentList:
            aux_payoff = 0
            gr = 0
            br = 0
            bp = 0
            ratio_rev = 0
            gr_last_time = 0
            aux_reputation = 0

            for i in range(tau, time + 1):
                paper = agent.manuscriptList[i]
                if paper.get("accepted") == 1:
                    journal_accepted = paper.get("journal")
                    jif = self.journalList[journal_accepted].jifList[time]
                    aux_payoff += jif
                    if paper['trueQuality'] == 1:
                        aux_reputation += jif
                    else:
                        bp += 1
                # gr = 0
                # br = 0
                gr_last_time = 0
                for review in agent.reviewlist[i]:
                    if review['trueQuality'] == review['reviewQuality']:
                        gr += 1
                        gr_last_time += 1
                    else:
                        br += 1
            if gr + br != 0:
                ratio_rev += gr / (gr + br)

            gp = 0
            if agent.manuscriptList[time].get("accepted") == 1 and agent.manuscriptList[time].get("trueQuality"):
                gp = 1

            payoff = aux_payoff - gr_last_time * sm.cost_review - gp * (
                    sm.cost_manuscript - sm.alpha_payoff * sm.cost_manuscript * ratio_rev)
            reputation = aux_reputation - sm.alpha_reputation * bp
            agent.payoff = payoff
            agent.publicReputation = reputation

    def evolve(self):
        """Evolution of agents and journals"""
        if sm.agents_evolve:
            for agent in self.agentList:
                own_evo = uniform(0, 1)
                if own_evo < sm.prob_agent_evo:
                    own_payoff = agent.payoff
                    better_agents = list(elem for elem in self.agentList if elem.payoff > own_payoff)
                    if len(better_agents) > 0:
                        better_agent_chosen = choice(better_agents)
                        features = list(vars(agent.reviewStrategy).keys())
                        features.append("manuscriptStrategy")
                        chosen_feature = choice(features)
                        if chosen_feature != "manuscriptStrategy":
                            val = getattr(better_agent_chosen.reviewStrategy, chosen_feature)
                            setattr(agent.reviewStrategy, chosen_feature, val)
                        else:
                            val = getattr(better_agent_chosen, chosen_feature)
                            setattr(agent, "manuscriptStrategy", val)

        if sm.journal_evolve:
            for i in self.journalList:
                own_evo = uniform(0, 1)
                if own_evo < sm.prob_journal_evo:
                    own_jif = i.jif
                    better_journals = list(j for j in self.journalList if j.jif > own_jif)
                    if len(better_journals) > 0:
                        better_journal_chosen = choice(better_journals)

                        features = ["disagreementStrategy", "maxPapers", "allowableSocialDist", "allowableTopicDist"]

                        chosen_feature = choice(features)

                        val = getattr(better_journal_chosen, chosen_feature)
                        setattr(i, chosen_feature, val)

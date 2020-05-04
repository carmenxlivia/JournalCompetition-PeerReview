import Model.model
import random
import Model.systemMetrics as sm
import pandas as pd
import numpy as np
import os

"""Main method used to start the model and save the results"""


def main():
    # CREATE THE "RESULTS" FOLDER
    root = os.getcwd()
    path = './Results'
    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)
    path_to_folder = os.getcwd()

    # SETTING THE SEED
    random.seed(pow(2, 19937) - 1)

    print("START: Initialise the model")

    # ------INITIALISE ALL THE VARIABLES NEEDED----
    empty_model = Model.model.PeerReviewModel(sm.no_agents, sm.no_journals)

    sm.maxSocialDist = empty_model.socialNetwork.maxSocialDist
    sm.minSocialDist = empty_model.socialNetwork.minSocialDist

    features = list(vars(empty_model.agentList[0].reviewStrategy).keys())
    features.append("manuscriptStrategy")

    features_journals = ['disagreementStrategy', 'maxPapers', 'allowableSocialDist', 'allowableTopicDist']

    size = int(sm.time / sm.select)
    payoff_df = pd.DataFrame()
    reputation_df = pd.DataFrame()

    jif_df = pd.DataFrame()
    acceptance_rate_df = pd.DataFrame()

    proportion_papers = [0] * size
    proportion_review = [0] * size

    feature_mean = {}
    feature_std = {}

    journal_feature_mean = {}
    journal_feature_std = {}

    for elem in features:
        feature_mean[elem] = [0] * size
        feature_std[elem] = [0] * size

    for elem in features_journals:
        journal_feature_mean[elem] = [0] * size
        journal_feature_std[elem] = [0] * size

    curr_payoffs = [0] * sm.no_agents
    curr_reputation = [0] * sm.no_agents
    attribute_vals = [0] * sm.no_agents

    attribute_journal_vals = [0] * sm.no_journals

    curr_jifs = [0] * sm.no_journals
    curr_acceptance_rate = [0] * sm.no_journals
    # --------------------------

    # Running the model
    for i in range(0, sm.time):
        print("------TIMESTEP: ", i)
        empty_model.step(i)
        empty_model.evolve()

        # Mean and Std of attributes
        if i % sm.select == 0:
            for elem in features:
                for agent in empty_model.agentList:
                    if elem != "manuscriptStrategy":
                        attribute_vals[agent.unique_id] = (getattr(agent.reviewStrategy, elem))
                    else:
                        attribute_vals[agent.unique_id] = (getattr(agent, elem))
                feature_mean[elem][int(i / sm.select)] = (np.mean(attribute_vals))
                feature_std[elem][int(i / sm.select)] = (np.std(attribute_vals))

            for elem in features_journals:
                for journal in empty_model.journalList:
                    attribute_journal_vals[journal.unique_id] = (getattr(journal, elem))
                journal_feature_mean[elem][int(i / sm.select)] = (np.mean(attribute_journal_vals))
                journal_feature_std[elem][int(i / sm.select)] = (np.std(attribute_journal_vals))

            # Proportions of good papers/good review over total
            gp = 0
            bp = 0
            gr = 0
            br = 0
            for agent in empty_model.agentList:
                if agent.manuscriptList[i].get("trueQuality") == 1:
                    gp += 1
                else:
                    bp += 1
                reviews_curr_time = agent.reviewlist[i]
                for review in reviews_curr_time:
                    if review.get("trueQuality") == review.get("reviewQuality"):
                        gr += 1
                    else:
                        br += 1
            proportion_papers[int(i / sm.select)] = (gp / (bp + gp))
            proportion_review[int(i / sm.select)] = (gr / (br + gr))

            # Journal JIFS and acceptance rates
            for journal in empty_model.journalList:
                curr_jifs[journal.unique_id] = journal.jif
                curr_acceptance_rate[journal.unique_id] = journal.acceptanceRate
            jif_df[int(i / sm.select)] = curr_jifs
            acceptance_rate_df[int(i / sm.select)] = curr_acceptance_rate

        # Reputation and Payoff of each agent
        if i > sm.time * 0.8:
            for author in empty_model.agentList:
                curr_payoffs[author.unique_id] = author.payoff
                curr_reputation[author.unique_id] = author.publicReputation
            payoff_df[i] = curr_payoffs
            reputation_df[i] = curr_reputation

        sm.maxReputation = empty_model.calculateMaxReputation()
        sm.minReputation = empty_model.calculateMinReputation()

    # ------CONVERT TO DATAFRAMES BEFORE SAVING TO CSV-----
    feature_mean_df = pd.DataFrame(feature_mean)
    feature_std_df = pd.DataFrame(feature_std)

    payoff_df = payoff_df.T

    reputation_df = reputation_df.T
    proportions_df = pd.DataFrame({'Proportion Papers': proportion_papers, 'Proportion Reviews': proportion_review})

    jif_df = jif_df.T
    acceptance_rate_df = acceptance_rate_df.T

    journal_feature_mean_df = pd.DataFrame(journal_feature_mean)
    journal_feature_std_df = pd.DataFrame(journal_feature_std)

    # --------------------------

    # ------SAVE ALL DATA TO DATAFRAMES-----
    reputation_df.to_csv(path_to_folder + "/REPUTATION.csv", encoding='utf-8', index=False)
    payoff_df.to_csv(path_to_folder + "/PAYOFF.csv", encoding='utf-8', index=False)
    feature_mean_df.to_csv(path_to_folder + "/MEAN_ATTRIBUTES.csv", encoding='utf-8', index=False)
    feature_std_df.to_csv(path_to_folder + "/STD_ATTRIBUTES.csv", encoding='utf-8', index=False)

    proportions_df.to_csv(path_to_folder + "/PROPORTIONS.csv", encoding='utf-8', index=False)
    jif_df.to_csv(path_to_folder + "/JIF.csv", encoding='utf-8', index=False)
    acceptance_rate_df.to_csv(path_to_folder + "/JOURNAL_ACCEPTANCE.csv", encoding='utf-8', index=False)

    journal_feature_mean_df.to_csv(path_to_folder + "/JOURNAL_MEAN_ATTRIBUTES.csv", encoding='utf-8', index=False)
    journal_feature_std_df.to_csv(path_to_folder + "/JOURNAL_STD_ATTRIBUTES.csv", encoding='utf-8', index=False)

    # --------------------------

    os.chdir(root)
    print("END: Run has ended")


if __name__ == "__main__":
    main()

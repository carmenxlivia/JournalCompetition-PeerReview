"""File of fixed variables. These will be used by other classes when imported
You can change the values of the variables"""

# Variables initialised - DO NOT CHANGE
maxReputation = 0
minReputation = 0
maxSocialDist = 0
minSocialDist = 0
select = 10

# Social network type
social_network_type = 1

# Set number of time steps of a simulation
time = 10000

# Set number of journals and agents
no_agents = 100
no_journals = 10

# Standard variables
cost_manuscript = 1
cost_review = 0.1
alpha_payoff = 1
alpha_reputation = 1
gamma = 1

time_window = 20

alpha_jif = 2

# Probabilities of evolution
prob_journal_evo = 0.01
prob_agent_evo = 0.05

# Turn on or off if you want agents or journals to have fixed attributes and strategies
fix_journals = True
fix_agents = False

# Turn on or of if you want to let the agents or journals evolve
journal_evolve = False
agents_evolve = True

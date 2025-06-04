##### The Problem
The purpose of this Python codebase is to explore the efficiency impact of restricted information sharing in greedy solutions to submodular maximization problems. To do this, the functions and algorithms below consider scenarios involving decision making agents that each select targets of differing values.

Each `Scenario` consists primarily of three things:
- A set of action sets that define which agents can select which targets
- A list of target values that define the value of each target
- A graph that determines how information regarding agent decisions is shared amongst agents

In this codebase, the objective for a given `Scenario` is to find an allowable assignment of agents to targets that maximizes the sum of the selected targets' values, where each target's value can be counted at most once. For any given assignment of agents to targets $x$, this sum is considered to be the *value of the assignment* and is denoted by $f(x)$.

The challenge of maximizing this objective function can be classified as a submodular maximization problem and is considered NP-Hard. There are therefore no efficient ways to determine the optimal assignment of agents to targets that maximize the objective function for any given scenario (unless of course $P = NP$).

That being said, it is known that a greedy algorithm is guaranteed to produce a solution at least half as good as the optimal solution. In such an algorithm, each agent sequentially picks the most valuable target allowed by it's action set and informs all other agents of the target it selected. Each agent's knowledge of past agents' decisions allows them to avoid picking targets that have already been selected (this approach is implemented below in the `distributed_greedy` function).

The issue with this approach is that in many real-world applications, it is unrealistic for each agent to have access to the decisions of all agents before it. How would the performance of a greedy algorithm change if agents could only inform a limited number of future agents of their choice of target (or maybe even a different agent's choice of target)? The purpose of this Python notebook is to explore this question.

##### Important Things to Know
The $i$-th agent is typically denoted as $x_i$ and the $i$-th target is typically denoted as $t_i$.

The efficiency of an assignment $x$ for a given `Scenario` is given by

$$\gamma(x) = \frac{f(x)}{f(x^{\text{opt}})}$$

where $f(x^{\text{opt}})$ is the value of an optimal assignment for the given `Scenario`.
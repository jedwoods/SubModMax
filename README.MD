### The Problem
The purpose of this Python codebase is to explore the efficiency impact of restricted information sharing in greedy solutions to submodular maximization problems. To do this, the functions and algorithms contained here consider scenarios involving decision making agents that each select targets of differing values.

Each `Scenario` consists primarily of three things:
- A set of action sets that define which agents can select which targets
- A list of target values that define the value of each target
- A graph that determines how information regarding agent decisions is shared amongst agents

In this codebase, the objective for a given `Scenario` is to find an allowable assignment of agents to targets that maximizes the sum of the selected targets' values, where each target's value can be counted at most once. For any given assignment of agents to targets $x$, this sum is considered to be the *value of the assignment* and is denoted by $f(x)$.

The challenge of maximizing this objective function can be classified as a submodular maximization problem and is considered NP-Hard. There are therefore no efficient ways to determine the optimal assignment of agents to targets that maximize the objective function for any given scenario (unless of course $P = NP$).

That being said, it is known that a greedy algorithm is guaranteed to produce a solution at least half as good as the optimal solution. In such an algorithm, each agent sequentially picks the most valuable target allowed by it's action set and informs all other agents of the target it selected. Each agent's knowledge of past agents' decisions allows them to avoid picking targets that have already been selected (this approach is implemented in the `distributed_greedy` function).

The issue with this approach is that in many real-world applications, it is unrealistic for each agent to have access to the decisions of all agents before it. How would the performance of a greedy algorithm change if agents could only inform a limited number of future agents of their choice of target (or maybe even a different agent's choice of target)? The purpose of this Python notebook is to explore this question.

Directed graphs (usually denoted by $G$, stored in each `Scenario` object) are used to model restricted information sharing between agents. In each directed graph of agents an edge from agent $A$ to agent $B$ indicates that agent $A$ can inform agent $B$ of either it’s own choice of target (which is the approach taken in the `generalized_distributed_greedy_rule` function) or the choice of a different agent in the `Scenario` that agent $A$ has knowledge of through the graph (which is demonstrated in the approach taken by the `highest_marginal_contribution_rule` function).

### Important Things to Know
While each agent understands the graph structure behind its own scenario and knows which agents are connected and how, agents cannot see the specific decisions and information being passed around outside of their own neighborhood. Agents make decisions in order (with agent 1 making its decision first). Once an agent has made a decision it cannot be changed. The information passed along is strictly limited to the target selected by one agent (as well as the agent that made that decision). Each agent must pass the same information to all of its outgoing neighbors (meaning an agent cannot pass different pieces of information to different neighbors). Agents are not allowed to know each others’ action sets, only their own.

### Notation

Assignments are typically denoted by $x$. The notation $x^{\text{sol}}$ is used to indicate a particular assignment of agents to targets within a scenario while $x^{\text{opt}}$ denotes an optimal assignment. Some scenarios have multiple optimal assignments.

$f(x)$ represents the value of an assignment $x$ in the context of a scenario. This is the submodular function that is to be maximized. In this codebase $f(x)$ is the sum of the target values of all of the *uniquely* selected targets.

The efficiency of an assignment $x$ for a given scenario is given by

$$\gamma(x) = \frac{f(x)}{f(x^{\text{opt}})}$$
The purpose of the $\texttt{lp\_generator.py}$ script is to create LPs that define submodular functions that result in the worst possible greedy algorithm efficiency (regardless of the information sharing rule used) for a given information sharing graph.

Below is an example of the LP that would be generated to define a worst-case submodular function $f$ and set of action classes $X$
for the information sharing graph $G = (V, E)$ where $V= [1, 2, 3]$ and $E = [(1, 2), (2, 3)]$. Each subset of the ground set becomes an LP
variable. For each agent, a greedy decision variable is created for every possible knowledge set that agent could receive.

$S = \{x_1^g, x_1^o, x_2^g, x_2^o, x_3^{g_1}, x_3^{g_2}\}\\$
$X_1 = \{x_1^g, x_1^o\}\\$
$X_2 = \{x_2^g, x_2^o\}\\$
$X_3 = \{x_3^{g_1}, x_3^{g_2}, x_3^o\}$

Goal: minimize $z$ subject to the following constraints:
1. $f(x_1^g) \ge f(x_1^o)$
2. $f(x_2^g | x_1^g) \ge f(x_2^o | x_1^g)$
3. $f(x_3^{g_1} | x_1^{g}) \ge f(x_3^o | x_1^g)$
4. $f(x_3^{g_1} | x_1^{g}) \ge f(x_3^{g_2} | x_1^g)$
5. $f(x_3^{g_2} | x_2^{g}) \ge f(x_3^o | x_2^g)$
6. $f(x_3^{g_2} | x_2^{g}) \ge f(x_3^{g_1} | x_2^g)$
7. $f(x_1^o, x_2^o, x_3^o) \ge f(A), \; \forall A \subseteq S$
8. $f(x_1^o, x_2^o, x_3^o) = 1$
9. $z \ge f(x_1^g, x_2^g, x_3^{g_1})$
10. $z \ge f(x_1^g, x_2^g, x_3^{g_2})$
11. $f$ must be submodular: $f(A \cup \{x\}) - f(A) \ge f(B \cup \{x\}) - f(B)$ for $A \subseteq B \subset S$ and $x \in S \setminus B$
12. $f$ must be monotone:  $f(A) \le f(B)$ for $A \subseteq B \subseteq S$
13. $f$ must be normalized: $f(\emptyset) = 0$

Constraints 1 through 6 are designed to "trick" the greedy algorithm into choosing agents that are locally appealing, but globally sub-optimal. They "push up" on the greedy solution. They capture the idea that agents can only pass one piece of information along an edge.

Constraints 7 and 8 define the optimal solution and assign it a value of $1$.

Constraints 9 and 10 "push down" on all of the possible greedy solutions.

Constraints 11 through 13 ensure that $f$ is submodular, monotonic, and normalized so as to meet the requirements of the problem at hand.

While listed as single constraints above, in reality constraints 7, 11, and 12 produce multiple constraints. Constraints 11 and 12 are implemented in a pairwise fashion so as to cut back on the number of computations and constraints needed to enforce submodularity and monotonicity.

Given any information sharing graph in $\mathcal{G} \coloneqq \{G = (V, E) : (i, j) \in E \Rightarrow i < j\}$, the script will generate and solve an LP similar to the one above that defines the worst case efficiency of the input graph (and the function $f$ that produced that worst case efficiency).

The time complexity of this script does not scale well as the complexity of the input graph increases. To counter this, a flag has been added to the script that "prunes" the LP. When the flag is set to true, the script only enforces submodularity, monotonicity, and optimality on subsets of the ground set that are actually possible as input to the function $f$ given the structure of the action classes. For example, in the scenairo outlined above, $f(x_1^g, x_1^o, x_2^o)$ is not a valid input to the function because each agent is only allowed to pick one decision variable from its action class (and in this case agent 1 picked two). In the pruned version of the LP, inputs like this are essentially ignored. It is unclear whether pruning the LP like this still guarantees the same worst case scenario efficiency bound.
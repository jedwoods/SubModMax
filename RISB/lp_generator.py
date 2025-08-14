import itertools
import networkx as nx
import cvxpy as cp
import os
from itertools import chain, combinations
from tabulate import tabulate
from datetime import datetime

# -----------------------
# Logging utilities
# -----------------------
logfile = None

def set_logfile(path: str):
    """Switch the current log output to a new file."""
    global logfile
    if logfile and not logfile.closed:
        logfile.close()
    logfile = open(path, "w", encoding="utf-8")

def logprint(*args, to_log=True, to_terminal=True, **kwargs):
    """Print to terminal and/or logfile."""
    if to_terminal:
        print(*args, **kwargs, flush=True)
    if to_log and logfile:
        print(*args, **kwargs, file=logfile, flush=True)

# -----------------------
# Graph utilities
# -----------------------
def generate_all_graphs_of_size_n(n: int):
    """Generate all directed graphs $G \in \mathcal{G}$ containing n nodes."""
    edges = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    all_subsets = [list(subset) for r in range(1, len(edges) + 1) for subset in combinations(edges, r)]
    results = []
    for edge_subset in all_subsets:
        G = nx.DiGraph()
        G.add_nodes_from(range(1, n + 1))
        G.add_edges_from(edge_subset)
        results.append(G)
    return results

def compute_info_sets_all_choices(G: nx.DiGraph):
    """
    Computes the possible knowledge sets receivable through information sharing by each agent
    in G.
    """
    G = G.copy()
    topo_order = list(nx.topological_sort(G))
    initial_state = {i: (frozenset(), None) for i in topo_order}
    all_info_sets = {i: set() for i in topo_order}
    queue = [initial_state]

    while queue:
        state = queue.pop()
        next_agent = next((i for i in topo_order if state[i][1] is None), None)
        if next_agent is None:
            for i in topo_order:
                all_info_sets[i].add(tuple(sorted(state[i][0])))
            continue

        knowledge_set = set(state[next_agent][0])
        own_choice_token = ("OWN", next_agent, tuple(sorted(knowledge_set)))
        possible_choices = sorted(
            list(knowledge_set) + [own_choice_token],
            key=lambda x: (str(type(x)), str(x))
        )

        for choice in possible_choices:
            new_state = {k: (set(v[0]), v[1]) for k, v in state.items()}
            new_state[next_agent] = (set(knowledge_set), choice)
            for nbr in sorted(G.successors(next_agent)):
                new_state[nbr][0].add(choice)
            new_state = {k: (frozenset(v[0]), v[1]) for k, v in new_state.items()}
            queue.append(new_state)

    greedy_vars = {}
    for agent in topo_order:
        sorted_ks_list = sorted(all_info_sets[agent], key=lambda ks: (len(ks), ks))
        greedy_vars[agent] = {ks: f"x{agent}g{idx}" for idx, ks in enumerate(sorted_ks_list, start=1)}

    final_info_sets = {}
    for agent in topo_order:
        agent_sets = set()
        for ks in all_info_sets[agent]:
            remapped = [
                greedy_vars[token[1]][token[2]] if isinstance(token, tuple) and token[0] == "OWN" else token
                for token in ks
            ]
            agent_sets.add(tuple(sorted(remapped)))
        final_info_sets[agent] = sorted(agent_sets, key=lambda x: (len(x), x))

    return final_info_sets

# -----------------------
# LP solver
# -----------------------
def build_and_solve_lp(G: nx.DiGraph, pruned: bool = False, info_sets=None):
    logprint(f"START TIME: {datetime.now().strftime('%m-%d-%Y %I:%M:%S %p')}")
    G = G.copy()
    mode_str = "PRUNED" if pruned else "FULL"
    logprint(f"Building {mode_str} LP for graph with {len(G.nodes())} agents and {len(G.edges())} edges.")
    logprint(f"Edge List:", G.edges(), to_terminal=False)

    logprint("\nEnsuring topological order...", to_log=False, end="")
    topo_order = list(nx.topological_sort(G))
    logprint(" done!", to_log=False)
    
    # Ground Set Generation
    logprint("Computing knowledge sets...", to_log=False, end="")
    if not info_sets:
        info_sets = compute_info_sets_all_choices(G)
    logprint(" done!", to_log=False)

    logprint("\nKnowledge Sets Receivable by Agents:", to_terminal=False)
    for agent in sorted(G.nodes()):
        sets_str = ", ".join("{" + ", ".join(s) + "}" for s in info_sets[agent])
        logprint(f" Agent {agent}: {sets_str}", to_terminal=False)

    logprint("Mapping LP variables...", to_log=False, end="")
    greedy_vars, opt_vars, all_vars = {}, {}, set()
    for i in topo_order:
        sets_for_agent = info_sets[i]
        greedy_vars[i] = {frozenset(ks): f"x{i}g{idx}" for idx, ks in enumerate(sets_for_agent, start=1)}
        opt_vars[i] = f"x{i}o"
        all_vars.update(greedy_vars[i].values())
        all_vars.add(opt_vars[i])
    all_vars = sorted(all_vars)

    subsets_to_iterate = None
    if pruned:
        feasible_profiles = list(itertools.product(
            *[list(greedy_vars[i].values()) + [opt_vars[i]] for i in topo_order]
        ))
        feasible_subsets = sorted(
            {frozenset(sub) for profile in feasible_profiles for r in range(len(profile) + 1)
             for sub in itertools.combinations(profile, r)},
            key=lambda s: (len(s), sorted(s))
        )
        subsets_to_iterate = feasible_subsets
    else:
        subsets_to_iterate = list(chain.from_iterable(combinations(all_vars, r) for r in range(len(all_vars) + 1)))

    subset_indices = {frozenset(s): idx for idx, s in enumerate(subsets_to_iterate)}
    f = cp.Variable(len(subsets_to_iterate))
    z = cp.Variable()

    def fval(*args):
        return f[subset_indices[frozenset(args)]]

    logprint(" done!", to_log=False)
    logprint(f"\nElements in Ground Set: {len(all_vars)}")
    logprint(f"Ground Set: {all_vars}", to_terminal=False)
    logprint(f"Total Variable Count: {len(subsets_to_iterate) + 1}", to_log=False)

    # Constraint Generation (see LPGEN_EXPLAINER.md for more details)
    constraints, counts = [], {}
    counts["Maximizing Greedy Locally"] = 0
    for i in topo_order:
        for ks, gvar in greedy_vars[i].items():
            constraints.append(fval(gvar, *ks) >= fval(opt_vars[i], *ks))
            counts["Maximizing Greedy Locally"] += 1
            for other_g in greedy_vars[i].values():
                if other_g != gvar:
                    constraints.append(fval(gvar, *ks) >= fval(other_g, *ks))
                    counts["Maximizing Greedy Locally"] += 1

    counts["Optimality"] = 0
    opt_profile = frozenset([opt_vars[i] for i in topo_order])
    constraints.append(f[subset_indices[opt_profile]] == 1)
    for s in subset_indices.keys():
        if s != opt_profile:
            constraints.append(f[subset_indices[opt_profile]] >= f[subset_indices[s]])
            counts["Optimality"] += 1

    counts["Minimizing Greedy Globally"] = 0
    for combo in itertools.product(*[list(greedy_vars[i].values()) for i in topo_order]):
        constraints.append(z >= f[subset_indices[frozenset(combo)]])
        counts["Minimizing Greedy Globally"] += 1

    counts["Submodularity"] = 0
    for A in subset_indices:
        for x in all_vars:
            if x in A:
                continue
            Ax = frozenset(set(A) | {x})
            if Ax not in subset_indices:
                continue
            for y in all_vars:
                if y in A or y == x:
                    continue
                By = set(A) | {y}
                Byx = frozenset(By | {x})
                if frozenset(By) not in subset_indices or Byx not in subset_indices:
                    continue
                constraints.append(f[subset_indices[Ax]] + f[subset_indices[frozenset(By)]] 
                                   >= f[subset_indices[Byx]] + f[subset_indices[A]])
                counts["Submodularity"] += 1

    counts["Monotonicity"] = 0
    for A in subset_indices:
        for x in all_vars:
            if x in A:
                continue
            B = frozenset(set(A) | {x})
            if B not in subset_indices:
                continue
            constraints.append(f[subset_indices[B]] >= f[subset_indices[A]])
            counts["Monotonicity"] += 1

    constraints.append(f[subset_indices[frozenset()]] == 0)
    counts["Normalization"] = 1

    logprint(f"Total Constraint Count: {len(constraints)}", to_log=False)

    # Solve
    logprint("\nCreating problem...", to_log=False, end="")
    problem = cp.Problem(cp.Minimize(z), constraints)
    logprint(" done!", to_log=False)

    logprint("Solving problem...", to_log=False, end="")
    problem.solve(solver=cp.GLPK)
    logprint(" done!", to_log=False)

    # Results
    logprint("\n- LP SUMMARY -", to_terminal=False)
    logprint(f"Variables: {len(subset_indices) + 1}", to_terminal=False)
    logprint(f"Constraints: {len(constraints)}", to_terminal=False)
    logprint(tabulate(counts.items(), headers=["Constraint Type", "Count"], tablefmt="simple"), to_terminal=False)

    logprint("\n- RESULTS -")
    logprint("Status:", problem.status)
    logprint("z =", z.value)
    logprint("See log file for function definition and more details.", to_log=False)

    logprint("\n- FUNCTION DEFINITION -", to_terminal=False)
    for s in subset_indices.keys():
        val = f[subset_indices[frozenset(s)]].value
        logprint(f"f({set(s)}) = {val:.5f}", to_terminal=False)

    logprint(f"END TIME: {datetime.now().strftime('%m-%d-%Y %I:%M:%S %p')}\n")
    return z.value, info_sets

# -----------------------
# Batch solver utilities
# -----------------------
def write_summary_table(headers: list, rows: list, path: str):
    with open(path, "w", encoding="utf-8") as f:
        print(tabulate(rows, headers=headers, tablefmt="simple"), file=f)

def solve_lp_cases(graph_set: list[nx.DiGraph], mode: str, output_dir: str):
    """Solve LPs for a set of graphs. mode: 'full', 'pruned', or 'both'."""
    os.makedirs(output_dir, exist_ok=True)
    total_cases = len(graph_set)
    print(f"Building and solving {mode.upper()} LPs for {total_cases} graphs...\n")
    results = {"full": {}, "pruned": {}}

    for idx, g in enumerate(graph_set, start=1):
        print(f"- - - CASE {idx} / {total_cases} - - -")
        info_sets = compute_info_sets_all_choices(g)

        if mode in ("full", "both"):
            set_logfile(f"{output_dir}/full_case{idx}.log" if mode == "both" else f"{output_dir}/case{idx}.log")
            results["full"][idx], _ = build_and_solve_lp(g, pruned=False, info_sets=info_sets)

        if mode in ("pruned", "both"):
            set_logfile(f"{output_dir}/pruned_case{idx}.log" if mode == "both" else f"{output_dir}/case{idx}.log")
            results["pruned"][idx], _ = build_and_solve_lp(g, pruned=True, info_sets=info_sets)

    if mode == "both":
        write_summary_table(
            ["Case #", "Full LP Solution", "Pruned LP Solution"],
            [[i, results["full"][i], results["pruned"][i]] for i in range(1, total_cases + 1)],
            os.path.join(output_dir, "comparison.txt")
        )
    else:
        label = "Full LP Solution" if mode == "full" else "Pruned LP Solution"
        write_summary_table(
            ["Case #", label],
            [[i, results[mode][i]] for i in range(1, total_cases + 1)],
            os.path.join(output_dir, "summary.txt")
        )
    print(f"\nFinished! See [{output_dir}] for detailed results.\n")
    return results

# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    solve_lp_cases(generate_all_graphs_of_size_n(3), mode="both", output_dir="RISB/3AgentGraphs")
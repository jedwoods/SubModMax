import itertools
import networkx as nx
import cvxpy as cp
import os
from itertools import chain, combinations
from tabulate import tabulate
from datetime import datetime

# Logging
logfile = open("default_log.log", "w", encoding="utf-8")
def logprint(*args, to_log=True, to_terminal=True, **kwargs):
    if to_terminal:
        print(*args, **kwargs, flush=True)
    if to_log:
        print(*args, **kwargs, file=logfile, flush=True)

def generate_all_graphs_of_size_n(n):
    edges = [(i , j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    all_subsets = [list(subset) for r in range(1, len(edges) + 1) for subset in combinations(edges, r)]
    results = []
    for edge_subset in all_subsets:
        G = nx.DiGraph()
        G.add_nodes_from([i for i in range(1, n + 1)])
        G.add_edges_from(edge_subset)
        results.append(G)
    return results

def compute_info_sets_all_choices(G):
    """
    Deterministic computation of knowledge sets for each agent.
    Uses tuple-based placeholders instead of fragile string parsing.
    """
    G = G.copy()
    topo_order = list(nx.topological_sort(G))
    initial_state = {i: (frozenset(), None) for i in topo_order}
    all_info_sets = {i: set() for i in topo_order}

    queue = [initial_state]

    while queue:
        state = queue.pop()

        # Find next agent in topo order who hasn't chosen yet
        next_agent = None
        for i in topo_order:
            if state[i][1] is None:
                next_agent = i
                break

        if next_agent is None:
            # Record final knowledge sets
            for i in topo_order:
                all_info_sets[i].add(tuple(sorted(state[i][0])))
            continue

        knowledge_set = set(state[next_agent][0])

        # Placeholder: tuple form avoids parsing ambiguity
        own_choice_token = ("OWN", next_agent, tuple(sorted(knowledge_set)))

        # Possible choices: any known item OR own decision
        possible_choices = sorted(
            list(knowledge_set) + [own_choice_token],
            key=lambda x: (str(type(x)), str(x))
        )

        for choice in possible_choices:
            # Deep copy
            new_state = {k: (set(v[0]), v[1]) for k, v in state.items()}
            new_state[next_agent] = (set(knowledge_set), choice)

            # Forward to all out-neighbors
            for nbr in sorted(G.successors(next_agent)):
                new_state[nbr][0].add(choice)

            # Freeze for immutability
            new_state = {k: (frozenset(v[0]), v[1]) for k, v in new_state.items()}
            queue.append(new_state)

    # Step 2: Assign deterministic g# labels
    greedy_vars = {}
    for agent in topo_order:
        sorted_ks_list = sorted(all_info_sets[agent], key=lambda ks: (len(ks), ks))
        greedy_vars[agent] = {}
        for idx, ks in enumerate(sorted_ks_list, start=1):
            gvarname = f"x{agent}g{idx}"
            greedy_vars[agent][ks] = gvarname

    # Step 3: Replace OWN(...) placeholders with g# labels
    final_info_sets = {}
    for agent in topo_order:
        agent_sets = set()
        for ks in all_info_sets[agent]:
            remapped = []
            for token in ks:
                if isinstance(token, tuple) and token[0] == "OWN":
                    agent_id = token[1]
                    inner_ks = token[2]
                    remapped.append(greedy_vars[agent_id][inner_ks])
                else:
                    remapped.append(token)
            agent_sets.add(tuple(sorted(remapped)))
        final_info_sets[agent] = sorted(agent_sets, key=lambda x: (len(x), x))

    return final_info_sets

def build_and_solve_lp(G: nx.DiGraph, pruned=False, info_sets=None):
    logprint(f"START TIME: {datetime.now().strftime('%m-%d-%Y %I:%M:%S %p')}")
    G = G.copy()
    pruned_string = "PRUNED" if pruned else "FULL"
    logprint(f"Building {pruned_string} LP for graph with {len(G.nodes())} agents and {len(G.edges())} edges.")
    logprint(f"Edge List:", G.edges(), to_terminal=False)
    
    logprint("\nEnsuring topological order...", to_log=False, end="")
    topo_order = list(nx.topological_sort(G))
    logprint(" done!", to_log=False)
    
    logprint("Computing knowledge sets...", to_log=False, end="")
    if not info_sets:
        info_sets = compute_info_sets_all_choices(G)
    logprint(" done!", to_log=False)

    logprint("\nKnowledge Sets Receivable by Agents:", to_terminal=False)
    for agent in sorted(G.nodes()):
        set_strings = []
        for s in info_sets[agent]:
            set_string = "{" + ", ".join(s) + "}"
            set_strings.append(set_string)
        logprint(f" Agent {agent}: {', '.join(set_strings)}", to_terminal=False)

    # Map LP variables
    logprint("Mapping LP variables...", to_log=False, end="")
    greedy_vars = {}
    opt_vars = {}
    all_vars = set()
    placeholder_to_actual = {}

    for i in topo_order:
        greedy_vars[i] = {}
        sets_for_agent = info_sets[i]
        for idx, ks in enumerate(sets_for_agent, start=1):
            gvarname = f"x{i}g{idx}"
            placeholder_to_actual[f"x{i}g"] = gvarname
            greedy_vars[i][frozenset(ks)] = gvarname
            all_vars.add(gvarname)
        optname = f"x{i}o"
        opt_vars[i] = optname
        all_vars.add(optname)

    # Remap knowledge sets to actual variable names
    remapped_greedy_vars = {}
    for i in topo_order:
        remapped_greedy_vars[i] = {}
        for ks, gvar in greedy_vars[i].items():
            remapped_ks = set()
            for item in ks:
                remapped_ks.add(placeholder_to_actual.get(item, item))
            remapped_greedy_vars[i][frozenset(remapped_ks)] = gvar
    greedy_vars = remapped_greedy_vars

    all_vars = sorted(all_vars)

    if pruned:
        # Pruned LP: feasible profiles only
        feasible_full_profiles = list(itertools.product(
            *[list(greedy_vars[i].values()) + [opt_vars[i]] for i in topo_order]
        ))
        feasible_subsets = set()
        for profile in feasible_full_profiles:
            for r in range(len(profile) + 1):
                for subset in itertools.combinations(profile, r):
                    feasible_subsets.add(frozenset(subset))

        feasible_subsets = sorted(feasible_subsets, key=lambda s: (len(s), sorted(s)))
        subset_indices = {frozenset(s): idx for idx, s in enumerate(feasible_subsets)}

        f = cp.Variable(len(feasible_subsets))
        logprint(" done!", to_log=False)
        logprint(f"\nElements in Ground Set: {len(all_vars)}")
        logprint(f"Ground Set: {all_vars}", to_terminal=False)
        logprint(f"Total Variable Count: {len(feasible_subsets) + 1}", to_log=False)

    else:
        # Full LP: all subsets of ground set
        subsets = list(chain.from_iterable(combinations(all_vars, r) for r in range(len(all_vars) + 1)))
        subset_indices = {frozenset(s): idx for idx, s in enumerate(subsets)}

        f = cp.Variable(len(subsets))
        logprint(" done!", to_log=False)
        logprint(f"\nElements in Ground Set: {len(all_vars)}")
        logprint(f"Ground Set: {all_vars}", to_terminal=False)
        logprint(f"Total Variable Count: {len(subsets) + 1}", to_log=False)

    z = cp.Variable()

    def fval(*args):
        return f[subset_indices[frozenset(args)]]

    logprint("Generating constraints...", to_log=False)
    constraints = []
    constraint_counts = {}

    # Step 3: Greedy ≥ optimal and greedy ≥ other greedy variants for same knowledge set
    logprint("    Maximizing greedy locally...", to_log=False, end="")
    constraint_counts["Maximizing Greedy Locally"] = 0
    for i in topo_order:
        for ks, gvar in greedy_vars[i].items():
            constraints.append(fval(gvar, *ks) >= fval(opt_vars[i], *ks))
            constraint_counts["Maximizing Greedy Locally"] += 1
            for other_g in greedy_vars[i].values():
                if other_g != gvar:
                    constraints.append(fval(gvar, *ks) >= fval(other_g, *ks))
                    constraint_counts["Maximizing Greedy Locally"] += 1
    logprint(f" {constraint_counts['Maximizing Greedy Locally']} constraints added.", to_log=False)

    # Step 4: Optimality constraints
    logprint("    Optimality...", to_log=False, end="")
    constraint_counts["Optimality"] = 0
    opt_profile = frozenset([opt_vars[i] for i in topo_order])
    if pruned:
        opt_idx = subset_indices[opt_profile]
    else:
        opt_idx = subset_indices[opt_profile]
    constraints.append(f[opt_idx] == 1)
    if pruned:
        subsets_to_iterate = feasible_subsets
    else:
        subsets_to_iterate = subset_indices.keys()
    for s in subsets_to_iterate:
        if s != opt_profile:
            constraints.append(f[opt_idx] >= f[subset_indices[s]])
            constraint_counts["Optimality"] += 1
    logprint(f" {constraint_counts['Optimality']} constraints added.", to_log=False)

    # Step 5: Minimize over all greedy profiles
    logprint("    Minimizing greedy globally...", to_log=False, end="")
    constraint_counts["Minimizing Greedy Globally"] = 0
    for combo in itertools.product(*[list(greedy_vars[i].values()) for i in topo_order]):
        constraints.append(z >= f[subset_indices[frozenset(combo)]])
        constraint_counts["Minimizing Greedy Globally"] += 1
    logprint(f" {constraint_counts['Minimizing Greedy Globally']} constraints added.", to_log=False)

    # Step 6: Submodularity constraints
    logprint("    Submodularity...", to_log=False, end="")
    constraint_counts["Submodularity"] = 0
    if pruned:
        subsets_to_iterate = feasible_subsets
    else:
        subsets_to_iterate = subset_indices.keys()

    for A in subsets_to_iterate:
        for x in all_vars:
            if x in A:
                continue
            A_union_x = frozenset(set(A) | {x})
            if A_union_x not in subset_indices:
                continue
            for y in all_vars:
                if y in A or y == x:
                    continue
                B_set = set(A) | {y}
                B_union_x = frozenset(B_set | {x})
                if frozenset(B_set) not in subset_indices:
                    continue
                if B_union_x not in subset_indices:
                    continue
                constraints.append(
                    f[subset_indices[A_union_x]] + f[subset_indices[frozenset(B_set)]] 
                    >= f[subset_indices[B_union_x]] + f[subset_indices[A]]
                )
                constraint_counts["Submodularity"] += 1
    logprint(f" {constraint_counts['Submodularity']} constraints added.", to_log=False)

    # Step 7: Monotonicity constraints
    logprint("    Monotonicity...", to_log=False, end="")
    constraint_counts["Monotonicity"] = 0
    if pruned:
        subsets_to_iterate = feasible_subsets
    else:
        subsets_to_iterate = subset_indices.keys()

    for A in subsets_to_iterate:
        for x in all_vars:
            if x in A:
                continue
            B = frozenset(set(A) | {x})
            if B not in subset_indices:
                continue
            constraints.append(f[subset_indices[B]] >= f[subset_indices[A]])
            constraint_counts["Monotonicity"] += 1
    logprint(f" {constraint_counts['Monotonicity']} constraints added.", to_log=False)

    # Step 8: Normalization
    logprint("    Normalization...", to_log=False, end="")
    constraints.append(f[subset_indices[frozenset()]] == 0)
    constraint_counts["Normalization"] = 1
    logprint(f" {constraint_counts['Normalization']} constraint added.", to_log=False)

    logprint(f"Total Constraint Count: {len(constraints)}", to_log=False)

    # Solve problem
    logprint("\nCreating problem...", to_log=False, end="")
    problem = cp.Problem(cp.Minimize(z), constraints)
    logprint(" done!", to_log=False)

    logprint("Solving problem...", to_log=False, end="")
    problem.solve(solver=cp.GLPK)
    logprint(" done!", to_log=False)

    # Results
    logprint("\n- LP SUMMARY -", to_terminal=False)
    if pruned:
        logprint(f"Variables: {len(feasible_subsets) + 1}", to_terminal=False)
    else:
        logprint(f"Variables: {len(subset_indices) + 1}", to_terminal=False)
    logprint(f"Constraints: {len(constraints)}", to_terminal=False)
    table = [(k, v) for k, v in constraint_counts.items()]
    logprint(tabulate(table, headers=["Constraint Type", "Count"], tablefmt="simple"), to_terminal=False)

    logprint("\n- RESULTS -")
    logprint("Status:", problem.status)
    logprint("z =", z.value)
    logprint("See log file for function definition and more details.", to_log=False)

    logprint("\n- FUNCTION DEFINITION -", to_terminal=False)
    if pruned:
        for s in feasible_subsets:
            val = f[subset_indices[frozenset(s)]].value
            logprint(f"f({set(s)}) = {val:.5f}", to_terminal=False)
    else:
        for s in subset_indices.keys():
            val = f[subset_indices[frozenset(s)]].value
            logprint(f"f({set(s)}) = {val:.5f}", to_terminal=False)

    logprint(f"END TIME: {datetime.now().strftime('%m-%d-%Y %I:%M:%S %p')}\n")
    return z.value, info_sets

def solve_lp_for_graph_set(graph_set: list[nx.DiGraph], pruned: bool, output_dir: str):
    global logfile
    total_cases = len(graph_set)
    case_nbr = 1
    results_dict = {}
    os.makedirs(output_dir, exist_ok=True)
    pruned_string = "PRUNED" if pruned else "FULL"
    print(f"Building and solving {pruned_string} LPs for {total_cases} graphs...\n")
    for g in graph_set:
        print(f"- - - CASE {case_nbr} / {total_cases} - - -")
        logfile = open(f"{output_dir}/case{case_nbr}.log", "w", encoding="utf-8")
        z, _ = build_and_solve_lp(g, pruned=pruned)
        results_dict[case_nbr] = z
        case_nbr += 1
    headers = ["Case #", f"{pruned_string} LP Solution"]
    rows = [[key, results_dict[key]] for key in range(1, total_cases + 1)]
    table_output = open(f"{output_dir}/summary.txt", "w", encoding="utf-8")
    print(tabulate(rows, headers=headers, tablefmt="simple"), file=table_output)
    print(f"\nFinished! See [{output_dir}] for detailed results.\n")
    return results_dict

def compare_lps_for_graph_set(graph_set: list[nx.DiGraph], output_dir: str):
    global logfile
    total_cases = len(graph_set)
    case_nbr = 1
    f_results = {}
    p_results = {}
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/full", exist_ok=True)
    os.makedirs(f"{output_dir}/pruned", exist_ok=True)
    print(f"Building and solving FULL and PRUNED LPs for {total_cases} graphs...\n")
    for g in graph_set:
        info_sets = compute_info_sets_all_choices(g)
        logfile = open(f"{output_dir}/full/case{case_nbr}.log", "w", encoding="utf-8")
        print(f"- - - CASE {case_nbr} / {total_cases} (FULL) - - -")
        z, _ = build_and_solve_lp(g, pruned=False, info_sets=info_sets)
        f_results[case_nbr] = z
        logfile = open(f"{output_dir}/pruned/case{case_nbr}.log", "w", encoding="utf-8")
        print(f"- - - CASE {case_nbr} / {total_cases} (PRUNED) - - -")
        z, _ = build_and_solve_lp(g, pruned=True, info_sets=info_sets)
        p_results[case_nbr] = z
        case_nbr += 1
    headers = ["Case #", "Full LP Solution", "Pruned LP Solution"]
    rows = [[key, f_results[key], p_results[key]] for key in range(1, total_cases + 1)]
    table_output = open(f"{output_dir}/comparison.txt", "w", encoding="utf-8")
    print(tabulate(rows, headers=headers, tablefmt="simple"), file=table_output)
    print(f"\nFinished! See [{output_dir}] for detailed results.\n")
    return f_results, p_results

if __name__ == "__main__":
    graph_set = generate_all_graphs_of_size_n(3)
    compare_lps_for_graph_set(graph_set, "RISB/3AgentAug7-2025")
    graph_set = generate_all_graphs_of_size_n(4)
    compare_lps_for_graph_set(graph_set, "RISB/4AgentAug7-2025")
    graph_set = generate_all_graphs_of_size_n(5)
    solve_lp_for_graph_set(graph_set, pruned=True, output_dir="RISB/5AgentPrunedAug7-2025")
import os
import csv
import tabulate
import numpy as np

def calc_stats(values: list[float]) -> dict[str, float]:
    return {
        'min': round(float(np.min(values)), 3),
        'max': round(float(np.max(values)), 3),
        'median': round(float(np.median(values)), 3),
        'mean': round(float(np.mean(values)), 3),
        'std_dev': round(float(np.std(values)), 3)
    }

def export_stat_dict_to_csv(stat_dict: dict[str, dict[str, dict[str, float]]], filename: str, out_directory: str) -> None:
    """
    Exports the stat_dict to a CSV file in the specified directory with the given filename.
    """
    rows = []
    for scenario, strategies in stat_dict.items():
        for strategy, stats in strategies.items():
            row = {
                'Scenario': scenario,
                'Strategy': strategy,
            }
            row.update(stats)
            rows.append(row)
    if not rows:
        print("No data to export.")
        return
    fieldnames = ['Scenario', 'Strategy'] + list(rows[0].keys())[2:]
    os.makedirs(out_directory, exist_ok=True)
    file_path = os.path.join(out_directory, filename)
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def print_stats(stat_dict: dict[str, dict[str, dict[str, float]]], statistic: str, file=None) -> None:
    """
    Prints a table for the provided statistic from the stat_dict. The statistic options are 'min', 'max', 
    'median', 'mean', and 'std_dev'.
    """
    if not stat_dict:
        print("No data to display.")
        return
    scenario_types = list(stat_dict.keys())
    algorithms = list(next(iter(stat_dict.values())).keys())
    headers = ["Scenario Type"] + algorithms
    table = []
    for stype in scenario_types:
        row = [stype]
        for alg in algorithms:
            value = stat_dict[stype][alg].get(statistic, None)
            row.append(round(value, 3) if value is not None else "N/A")
        table.append(row)
    print(file=file)
    print(tabulate.tabulate(table, headers=headers, tablefmt="plain"), file=file)
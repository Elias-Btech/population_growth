import os

from config import RESULTS_DIR
from experiments import (
    generate_dataset,
    run_fibonacci_experiments, run_power_experiments, run_dataset_experiments,
    print_fibonacci_results, print_population_results, print_summary,
    save_fibonacci_csv, save_population_csv, save_dataset_results_csv,
    plot_fibonacci_times, plot_power_times, plot_population_growth,
)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("\n" + "=" * 74)
    print("Iterative vs Recursive Population Growth Prediction")
    print("=" * 74)

    print("\n  [1] Generating 1000-record input dataset …")
    generate_dataset()

    print("  [2] Running Fibonacci experiments …")
    fib_rows = run_fibonacci_experiments()

    print("  [3] Running Power experiments (Iterative / Recursive / D&C) …")
    power_rows = run_power_experiments()

    print("  [4] Running dataset experiment (1000 records from CSV) …")
    dataset_rows = run_dataset_experiments()

    print_fibonacci_results(fib_rows)
    print_population_results(power_rows)
    print_summary(fib_rows, power_rows)

    print("  Saving CSV files …")
    save_fibonacci_csv(fib_rows)
    save_population_csv(power_rows)
    save_dataset_results_csv(dataset_rows)

    print("\n  Generating charts …")
    plot_fibonacci_times(fib_rows)
    plot_power_times(power_rows)
    plot_population_growth(power_rows)

    print("\n  Done.\n")


if __name__ == "__main__":
    main()

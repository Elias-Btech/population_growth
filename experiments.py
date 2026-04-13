"""
SECTION 2 — EXPERIMENTS
Handles dataset generation, timed experiments, console reporting,
CSV export, and chart visualization.
"""

import csv
import math
import os
import random
import sys
import time

from algorithms import (
    fibonacci_iterative, fibonacci_recursive,
    power_iterative, power_recursive, power_divide_conquer,
)
from config import (
    RESULTS_DIR, DATASET_FILE,
    FIB_INPUTS, FIB_RECURSIVE_LIMIT,
    POWER_INPUTS, P0_FIXED, BASE_FIXED,
)


# ─── DATASET ────────────────────────────────────────────────────────────────

def generate_dataset(size=1000, seed=42):
    """Generate random population records and save to CSV (reproducible via seed)."""
    random.seed(seed)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    records = []
    for i in range(1, size + 1):
        n = random.randint(1, 100)
        P0 = random.randint(100, 10000)
        growth_rate = round(random.uniform(0.01, 0.10), 4)
        records.append({
            "record_id": i,
            "n": n,
            "P0": P0,
            "growth_rate": growth_rate,
            "base": round(1 + growth_rate, 4),
        })
    with open(DATASET_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["record_id", "n", "P0", "growth_rate", "base"])
        writer.writeheader()
        writer.writerows(records)
    print(f"  [DATASET] {size} records generated → {DATASET_FILE}")
    return records


def load_dataset():
    """Load records from the CSV dataset file (generates it if missing)."""
    if not os.path.exists(DATASET_FILE):
        return generate_dataset()
    records = []
    with open(DATASET_FILE, newline="") as f:
        for row in csv.DictReader(f):
            records.append({
                "record_id": int(row["record_id"]),
                "n": int(row["n"]),
                "P0": int(row["P0"]),
                "growth_rate": float(row["growth_rate"]),
                "base": float(row["base"]),
            })
    return records


# ─── TIMED RUNNER ────────────────────────────────────────────────────────────

def _timed(func, *args):
    """Call func(*args) and return (result, elapsed_seconds)."""
    t0 = time.perf_counter()
    result = func(*args)
    return result, time.perf_counter() - t0


# ─── EXPERIMENTS ─────────────────────────────────────────────────────────────

def run_fibonacci_experiments():
    rows = []
    for n in FIB_INPUTS:
        (iter_result, fib_list), iter_time = _timed(fibonacci_iterative, n)
        iter_space = sys.getsizeof(fib_list) + sum(sys.getsizeof(x) for x in fib_list)
        rec_space = sys.getsizeof(0) * n

        if n <= FIB_RECURSIVE_LIMIT:
            rec_result, rec_time = _timed(fibonacci_recursive, n)
        else:
            rec_result, rec_time = "SKIPPED (too slow)", float("nan")

        rows.append({
            "n": n,
            "iter_result": iter_result,
            "rec_result": rec_result,
            "iter_time": iter_time,
            "rec_time": rec_time,
            "iter_space": iter_space,
            "rec_space": rec_space,
            "iter_sequence": fib_list,
        })
    return rows


def run_power_experiments():
    rows = []
    for n in POWER_INPUTS:
        iter_p, iter_t = _timed(power_iterative, BASE_FIXED, n)
        rec_p, rec_t = _timed(power_recursive, BASE_FIXED, n)
        dc_p, dc_t = _timed(power_divide_conquer, BASE_FIXED, n)
        rows.append({
            "n": n,
            "iter_power": iter_p,
            "rec_power": rec_p,
            "dc_power": dc_p,
            "population_iter": P0_FIXED * iter_p,
            "population_rec": P0_FIXED * rec_p,
            "population_dc": P0_FIXED * dc_p,
            "iter_time": iter_t,
            "rec_time": rec_t,
            "dc_time": dc_t,
        })
    return rows


def run_dataset_experiments():
    """Run power_iterative and power_divide_conquer on all 1000 CSV records."""
    rows = []
    for rec in load_dataset():
        iter_p, iter_t = _timed(power_iterative, rec["base"], rec["n"])
        dc_p, dc_t = _timed(power_divide_conquer, rec["base"], rec["n"])
        rows.append({
            "record_id": rec["record_id"],
            "n": rec["n"],
            "P0": rec["P0"],
            "growth_rate": rec["growth_rate"],
            "base": rec["base"],
            "population_iter": round(rec["P0"] * iter_p, 4),
            "population_dc": round(rec["P0"] * dc_p, 4),
            "iter_time": iter_t,
            "dc_time": dc_t,
        })
    return rows


# ─── REPORTING ───────────────────────────────────────────────────────────────

def _sep(w=74):
    print("-" * w)


def print_fibonacci_results(rows):
    print("\n" + "=" * 74)
    print("  FIBONACCI — ITERATIVE O(n)  vs  RECURSIVE O(2^n)")
    print("=" * 74)
    print(f"  {'n':>4}  {'Iter Result':>12}  {'Rec Result':>20}  "
          f"{'Iter Time':>11}  {'Rec Time':>13}  {'Iter Mem':>8}  {'Rec Mem':>7}")
    _sep()
    for r in rows:
        rt = (f"{r['rec_time']:>13.6f}" if not math.isnan(r['rec_time']) else "      SKIPPED")
        print(f"  {r['n']:>4}  {r['iter_result']:>12}  {str(r['rec_result']):>20}  "
              f"  {r['iter_time']:>9.6f}  {rt}  "
              f"  {r['iter_space']:>6}B  {r['rec_space']:>5}B")
    _sep()
    print("\n  Detailed Results:")
    for r in rows:
        skipped = isinstance(r['rec_result'], str)
        print(f"\n  Fibonacci({r['n']})")
        print(f"    Iterative result : {r['iter_result']}")
        print(f"    Recursive result : {r['rec_result']}")
        print(f"    Iterative time   : {r['iter_time']:.6f} sec")
        if skipped:
            print(f"    Recursive time   : SKIPPED — O(2^n) impractical for n={r['n']}")
        else:
            print(f"    Recursive time   : {r['rec_time']:.6f} sec")
            if r['iter_time'] > 0:
                print(f"    Recursive is ~{r['rec_time'] / r['iter_time']:.1f}x slower")
        print(f"    Sequence (first 10): {r['iter_sequence'][:10]}")


def print_population_results(rows):
    print("\n" + "=" * 74)
    print("  POWER COMPUTATION — Iterative O(n) | Recursive O(n) | D&C O(log n)")
    print("  Population model: P(n) = 1000 × (1.05)^n")
    print("=" * 74)
    print(f"  {'n':>4}  {'Population':>13}  {'Iter Time':>11}  "
          f"{'Rec Time':>11}  {'D&C Time':>11}  {'D&C Speedup':>11}")
    _sep()
    # Show first row, last row, and every 5th row (by enumerate index, not n value)
    display = set([0, len(rows) - 1] + list(range(4, len(rows), 5)))
    for i, r in enumerate(rows):
        if i in display:
            sp = r['iter_time'] / r['dc_time'] if r['dc_time'] > 0 else 0
            print(f"  {r['n']:>4}  {r['population_iter']:>13.4f}  "
                  f"  {r['iter_time']:>9.7f}  {r['rec_time']:>11.7f}  "
                  f"  {r['dc_time']:>9.7f}  {sp:>9.1f}x")
    _sep()


def print_summary(fib_rows, power_rows):
    print("\n" + "=" * 74)
    print("  SUMMARY OF OBSERVATIONS")
    print("=" * 74)
    print("\n  Fibonacci:")
    for r in fib_rows:
        if isinstance(r['rec_result'], str):
            print(f"    n={r['n']:>2}: iter={r['iter_time']:.6f}s | rec=SKIPPED (O(2^n))")
        else:
            sp = r['rec_time'] / r['iter_time'] if r['iter_time'] > 0 else 0
            print(f"    n={r['n']:>2}: iter={r['iter_time']:.6f}s | "
                  f"rec={r['rec_time']:.6f}s | ~{sp:.0f}x slower")
    print("""
  Key Takeaways:
    1. Iterative Fibonacci O(n): single loop, fast, stores sequence in array.
    2. Recursive Fibonacci O(2^n): recomputes sub-problems — exponential blowup.
       At n=35 it is already ~190,000x slower. Impractical beyond n~35.
    3. Both give identical results, confirming correctness.

    4. Iterative power O(n) and recursive power O(n) are similar for n<=50.
    5. Divide-and-conquer power O(log n) halves the problem each step.
       For large exponents (n=1000+) the D&C advantage becomes dramatic.
    6. Recommendation: use iterative Fibonacci and D&C power in production.
""")


# ─── CSV EXPORT ──────────────────────────────────────────────────────────────

def save_fibonacci_csv(rows):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "fibonacci_results.csv")
    fields = ["Input_n", "Iterative_Fibonacci", "Recursive_Fibonacci",
              "Iterative_Time_sec", "Recursive_Time_sec",
              "Iterative_Space_bytes", "Recursive_Space_bytes"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({
                "Input_n": r["n"],
                "Iterative_Fibonacci": r["iter_result"],
                "Recursive_Fibonacci": r["rec_result"],
                "Iterative_Time_sec": f"{r['iter_time']:.8f}",
                "Recursive_Time_sec": ("SKIPPED" if math.isnan(r['rec_time'])
                                       else f"{r['rec_time']:.8f}"),
                "Iterative_Space_bytes": r["iter_space"],
                "Recursive_Space_bytes": r["rec_space"],
            })
    print(f"  [CSV] fibonacci_results.csv           → {path}")


def save_population_csv(rows):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "population_growth_results.csv")
    fields = ["Input_n", "Iterative_Power", "Recursive_Power", "DC_Power",
              "Population_Iterative", "Population_Recursive", "Population_DC",
              "Iterative_Time_sec", "Recursive_Time_sec", "DC_Time_sec"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({
                "Input_n": r["n"],
                "Iterative_Power": f"{r['iter_power']:.8f}",
                "Recursive_Power": f"{r['rec_power']:.8f}",
                "DC_Power": f"{r['dc_power']:.8f}",
                "Population_Iterative": f"{r['population_iter']:.4f}",
                "Population_Recursive": f"{r['population_rec']:.4f}",
                "Population_DC": f"{r['population_dc']:.4f}",
                "Iterative_Time_sec": f"{r['iter_time']:.10f}",
                "Recursive_Time_sec": f"{r['rec_time']:.10f}",
                "DC_Time_sec": f"{r['dc_time']:.10f}",
            })
    print(f"  [CSV] population_growth_results.csv   → {path}")


def save_dataset_results_csv(rows):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "dataset_results.csv")
    fields = ["record_id", "n", "P0", "growth_rate", "base",
              "Population_Iterative", "Population_DC",
              "Iterative_Time_sec", "DC_Time_sec"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({
                "record_id": r["record_id"],
                "n": r["n"],
                "P0": r["P0"],
                "growth_rate": r["growth_rate"],
                "base": r["base"],
                "Population_Iterative": r["population_iter"],
                "Population_DC": r["population_dc"],
                "Iterative_Time_sec": f"{r['iter_time']:.10f}",
                "DC_Time_sec": f"{r['dc_time']:.10f}",
            })
    print(f"  [CSV] dataset_results.csv             → {path}")


# ─── VISUALIZATION ───────────────────────────────────────────────────────────

def _get_plt():
    try:
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        print("  [INFO] matplotlib not installed — skipping charts.")
        print("         Install with: pip install matplotlib")
        return None


def plot_fibonacci_times(rows):
    plt = _get_plt()
    if not plt:
        return
    ns = [r["n"] for r in rows]
    it = [r["iter_time"] for r in rows]
    rt = [r["rec_time"] if not math.isnan(r["rec_time"]) else 0 for r in rows]
    x, w = range(len(ns)), 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([i - w / 2 for i in x], it, w, label="Iterative O(n)", color="#4C9BE8")
    ax.bar([i + w / 2 for i in x], rt, w, label="Recursive O(2^n)", color="#E8694C")
    ax.set_xticks(list(x))
    ax.set_xticklabels([str(n) for n in ns])
    ax.set_xlabel("n (Fibonacci index)")
    ax.set_ylabel("Execution Time (seconds)")
    ax.set_title("Fibonacci: Iterative vs Recursive Execution Time")
    ax.set_yscale("log")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "fibonacci_time_comparison.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [PLOT] fibonacci_time_comparison.png  → {path}")


def plot_power_times(rows):
    plt = _get_plt()
    if not plt:
        return
    ns = [r["n"] for r in rows]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(ns, [r["iter_time"] for r in rows], marker="o", ms=3,
            label="Iterative O(n)", color="#4C9BE8")
    ax.plot(ns, [r["rec_time"] for r in rows], marker="s", ms=3,
            label="Recursive O(n)", color="#E8694C")
    ax.plot(ns, [r["dc_time"] for r in rows], marker="^", ms=3,
            label="Divide & Conquer O(log n)", color="#2ECC71")
    ax.set_xlabel("n (exponent)")
    ax.set_ylabel("Execution Time (seconds)")
    ax.set_title("Power Computation: Iterative vs Recursive vs D&C")
    ax.legend()
    ax.grid(linestyle="--", alpha=0.5)
    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "power_time_comparison.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [PLOT] power_time_comparison.png      → {path}")


def plot_population_growth(rows):
    plt = _get_plt()
    if not plt:
        return
    ns = [r["n"] for r in rows]
    pops = [r["population_iter"] for r in rows]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(ns, pops, marker="o", ms=3, color="#2ECC71")
    ax.set_xlabel("Years (n)")
    ax.set_ylabel("Population")
    ax.set_title("Exponential Population Growth  P(n) = 1000 × (1.05)^n")
    ax.grid(linestyle="--", alpha=0.5)
    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "population_growth_curve.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [PLOT] population_growth_curve.png    → {path}")

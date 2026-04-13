"""
Shared configuration: paths and experiment constants.
"""

import os
import sys

sys.setrecursionlimit(10_000)

# Always resolve paths relative to this file's location
_BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR  = os.path.join(_BASE_DIR, "results")
DATASET_FILE = os.path.join(RESULTS_DIR, "population_dataset.csv")

# Fixed test inputs
FIB_INPUTS = [10, 20, 30, 35, 40, 45]
FIB_RECURSIVE_LIMIT = 35    # recursive Fibonacci skipped beyond this (O(2^n) too slow)
POWER_INPUTS = list(range(1, 51))
P0_FIXED = 1000
BASE_FIXED = 1.05  # 5% growth rate

"""
SECTION 1 — ALGORITHMS
Fibonacci and Power computation using iterative, recursive, and divide-and-conquer approaches.
"""


def fibonacci_iterative(n):
    """
    Compute F(n) using a loop and store the full sequence in a list.
    Time  complexity : O(n)  — one pass through n iterations
    Space complexity : O(n)  — list holds all n+1 values
    """
    if n == 0:
        return 0, [0]
    if n == 1:
        return 1, [0, 1]
    fib = [0, 1]
    for i in range(2, n + 1):
        fib.append(fib[i - 1] + fib[i - 2])  # recurrence: F(n) = F(n-1) + F(n-2)
    return fib[n], fib


def fibonacci_recursive(n):
    """
    Compute F(n) using plain recursion (no memoization).
    Time  complexity : O(2^n) — each call branches into two sub-calls.
    Space complexity : O(n)   — maximum call-stack depth equals n.
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def power_iterative(base, n):
    """
    Compute base^n by multiplying in a loop.
    Time  complexity : O(n)  — exactly n multiplications
    Space complexity : O(1)  — only two variables used
    """
    result = 1.0
    for _ in range(n):
        result *= base
    return result


def power_recursive(base, n):
    """
    Compute base^n using simple recursion.
    Time  complexity : O(n)  — n recursive calls
    Space complexity : O(n)  — call stack grows to depth n
    """
    if n == 0:
        return 1.0
    return base * power_recursive(base, n - 1)


def power_divide_conquer(base, n):
    """
    Compute base^n using divide-and-conquer (fast exponentiation).
    Time  complexity : O(log n) — problem halves at every even step
    Space complexity : O(log n) — call-stack depth is log2(n)
    """
    if n == 0:
        return 1.0
    if n % 2 == 0:
        half = power_divide_conquer(base, n // 2)
        return half * half
    return base * power_divide_conquer(base, n - 1)

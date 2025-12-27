# -*- coding: utf-8 -*-

"""
Performance tests for Tix iteration methods.

Parameterized tests with 999, 9,999, and 99,999 total items (stories + tasks)
to measure scanning performance at different scales. Each story has 3-5 tasks
randomly assigned. Each test uses a separate directory and cleans up
automatically after completion.

Benchmark: 29,510 items/s
"""

import time
import random
import shutil
from pathlib import Path

from shai_tix.tix import Tix
from shai_tix.paths import path_enum
from shai_tix.constants import ZERO_PADDING, WordsEnum


def format_number(n: int) -> str:
    """Format number with comma separators for readability."""
    return f"{n:,}"


def format_duration(seconds: float) -> str:
    """Format duration in human-friendly format."""
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"


def print_header(title: str, char: str = "=", width: int = 70):
    """Print a formatted header."""
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")


def print_metric(label: str, value: str, indent: int = 2):
    """Print a formatted metric."""
    print(f"{' ' * indent}{label:<25} {value}")


def create_test_fixture(dir_tix: Path, total_items: int) -> dict:
    """
    Create test fixture with exactly total_items stories and tasks.

    Distributes total_items between stories and tasks, where each story
    has 3-5 tasks randomly assigned. The last story gets remaining items
    to ensure exact total count.

    :param dir_tix: Root directory for .tix
    :param total_items: Exact total number of items (stories + tasks)

    :returns: Dictionary with counts {stories, tasks, total}
    """
    dir_stories = dir_tix / WordsEnum.stories.value

    print(f"\n  Target: exactly {format_number(total_items)} items")

    start = time.perf_counter()

    random.seed(42)  # Reproducible results
    current_id = 1
    actual_stories = 0
    actual_tasks = 0
    remaining = total_items

    while remaining > 0:
        # Need at least 1 story + 1 task
        if remaining < 2:
            break

        # Create story folder
        story_id = str(current_id).zfill(ZERO_PADDING)
        story_folder = dir_stories / f"story-2025-01-01-{story_id}-test-story-{current_id}"
        story_folder.mkdir(parents=True, exist_ok=True)
        current_id += 1
        actual_stories += 1
        remaining -= 1

        # Determine number of tasks for this story
        if remaining <= 5:
            # Last story: use all remaining as tasks
            num_tasks = remaining
        else:
            # Leave room for future stories (min 4 items: 1 story + 3 tasks)
            max_allowed = remaining - 4 if remaining > 9 else remaining
            num_tasks = min(random.randint(3, 5), max_allowed)

        tasks_dir = story_folder / WordsEnum.tasks.value
        for _ in range(num_tasks):
            task_id = str(current_id).zfill(ZERO_PADDING)
            task_folder = tasks_dir / f"task-2025-01-01-{task_id}-test-task-{current_id}"
            task_folder.mkdir(parents=True, exist_ok=True)
            current_id += 1
            actual_tasks += 1
            remaining -= 1

    elapsed = time.perf_counter() - start
    actual_total = actual_stories + actual_tasks
    rate = actual_total / elapsed if elapsed > 0 else 0

    print(f"  Created {format_number(actual_stories)} stories + {format_number(actual_tasks)} tasks = {format_number(actual_total)} items")
    print(f"  Time: {format_duration(elapsed)} ({format_number(int(rate))} items/s)")
    print(f"  Avg tasks per story: {actual_tasks / actual_stories:.1f}")

    return {
        "stories": actual_stories,
        "tasks": actual_tasks,
        "total": actual_total,
    }


def run_benchmark(tix: Tix, num_iterations: int = 5) -> dict:
    """
    Run benchmark iterations and collect timing statistics.

    :param tix: Tix instance to benchmark
    :param num_iterations: Number of benchmark iterations

    :returns: Dictionary with benchmark results
    """
    # Warmup run (not counted)
    print("\n  Warmup run...")
    _ = list(tix.iter_stories_or_tasks())

    # Benchmark runs
    print(f"\n  Benchmark runs ({num_iterations} iterations):")
    times = []
    item_count = 0

    for i in range(num_iterations):
        start = time.perf_counter()
        items = list(tix.iter_stories_or_tasks())
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        item_count = len(items)
        print(f"    Run {i + 1}: {format_number(item_count)} items in {format_duration(elapsed)}")

    return {
        "item_count": item_count,
        "times": times,
        "avg": sum(times) / len(times),
        "min": min(times),
        "max": max(times),
    }


def run_individual_benchmarks(tix: Tix) -> dict:
    """
    Benchmark individual iteration methods.

    :param tix: Tix instance to benchmark

    :returns: Dictionary with method-specific results
    """
    results = {}

    # iter_stories
    start = time.perf_counter()
    stories = list(tix.iter_stories())
    elapsed = time.perf_counter() - start
    results["iter_stories"] = {"count": len(stories), "time": elapsed}

    # iter_tasks
    start = time.perf_counter()
    tasks = list(tix.iter_tasks())
    elapsed = time.perf_counter() - start
    results["iter_tasks"] = {"count": len(tasks), "time": elapsed}

    # iter_stories_or_tasks
    start = time.perf_counter()
    all_items = list(tix.iter_stories_or_tasks())
    elapsed = time.perf_counter() - start
    results["iter_stories_or_tasks"] = {"count": len(all_items), "time": elapsed}

    return results


def run_scale_test(total_items: int, test_name: str):
    """
    Run a complete performance test at a specific scale.

    :param total_items: Target total number of items (stories + tasks)
    :param test_name: Human-readable test name for logging
    """
    dir_tix = path_enum.dir_tmp / f".tix-perf-{total_items}"

    print_header(f"Performance Test: {test_name}", "=")
    print(f"\n  Test directory: {dir_tix}")

    try:
        # Clean up any existing directory
        if dir_tix.exists():
            shutil.rmtree(dir_tix)

        # Create fixture
        fixture_stats = create_test_fixture(dir_tix, total_items)

        # Create Tix instance
        tix = Tix(dir_root=dir_tix)

        # Run main benchmark
        results = run_benchmark(tix, num_iterations=5)

        # Print summary
        print_header("Results Summary", "-", 50)
        print_metric("Stories:", format_number(fixture_stats["stories"]))
        print_metric("Tasks:", format_number(fixture_stats["tasks"]))
        print_metric("Total items:", format_number(results["item_count"]))
        print_metric("Average time:", format_duration(results["avg"]))
        print_metric("Min time:", format_duration(results["min"]))
        print_metric("Max time:", format_duration(results["max"]))
        print_metric("Throughput:", f"{format_number(int(results['item_count'] / results['avg']))} items/s")

        # Run individual method benchmarks
        print_header("Individual Method Performance", "-", 50)
        individual = run_individual_benchmarks(tix)

        for method, data in individual.items():
            rate = data["count"] / data["time"] if data["time"] > 0 else 0
            print_metric(
                f"{method}():",
                f"{format_number(data['count'])} items in {format_duration(data['time'])} ({format_number(int(rate))}/s)"
            )

    finally:
        # Cleanup
        print(f"\n  Cleaning up {dir_tix}...")
        if dir_tix.exists():
            shutil.rmtree(dir_tix)
        print("  Done.")


def run_all_performance_tests():
    """Run all parameterized performance tests."""
    test_configs = [
        # (999, "Small Scale (999 items)"),
        (9_999, "Medium Scale (9,999 items)"),
        # (99_999, "Large Scale (99,999 items)"),
    ]

    print_header("TIX PERFORMANCE TEST SUITE", "█", 70)
    print(f"\n  Running {len(test_configs)} scale tests...")
    print(f"  ID format: {ZERO_PADDING}-digit zero-padded")
    print(f"  Each story has 3-5 tasks (random)")

    total_start = time.perf_counter()

    for total_items, test_name in test_configs:
        run_scale_test(total_items, test_name)
        print()  # Add spacing between tests

    total_elapsed = time.perf_counter() - total_start

    print_header("ALL TESTS COMPLETED", "█", 70)
    print(f"\n  Total test time: {format_duration(total_elapsed)}")
    print()


if __name__ == "__main__":
    run_all_performance_tests()

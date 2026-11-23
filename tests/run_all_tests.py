"""AI Code Review & Security Analysis Agent - Test Suite Runner.

Executes all unit, integration, RAG, and report tests using Python standard
unittest. Compatible with pytest or direct execution via `python tests/run_all_tests.py`.
"""
import os
import sys
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def run_tests():
    """Discover and execute all test cases in the tests directory."""
    print("=" * 65)
    print("AI CODE REVIEW & SECURITY ANALYSIS AGENT - TEST SUITE RUNNER")
    print("=" * 65)

    tests_dir = os.path.join(PROJECT_ROOT, "tests")
    suite = unittest.defaultTestLoader.discover(start_dir=tests_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    result = runner.run(suite)

    total_run = result.testsRun
    failed = len(result.failures)
    errors = len(result.errors)
    passed = total_run - (failed + errors)

    print("\n" + "=" * 65)
    print(f"TEST EXECUTION SUMMARY: {passed} Passed, {failed} Failed, {errors} Errors (Total: {total_run})")
    print("=" * 65)

    if failed == 0 and errors == 0:
        print("[SUCCESS] All tests passed cleanly!")
        return 0
    else:
        print("[FAILURE] Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())

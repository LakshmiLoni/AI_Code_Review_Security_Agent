"""Standalone Test Runner.

Executes all test functions across the test suite using standard library
without requiring third-party test runners. Can also be invoked with pytest.
"""
import sys
import os
import inspect
import traceback

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import tests.test_language_detector as t_lang
import tests.test_code_analysis as t_code
import tests.test_security_agent as t_sec
import tests.test_remediation as t_rem
import tests.test_orchestrator as t_orch
import tests.test_knowledge_base as t_kb
import tests.test_routes as t_routes


def run_module_tests(module, module_name):
    print(f"\nRunning tests in {module_name}...")
    functions = [
        obj for name, obj in inspect.getmembers(module, inspect.isfunction)
        if name.startswith("test_")
    ]
    passed = 0
    failed = 0

    for fn in functions:
        fn_name = fn.__name__
        try:
            fn()
            print(f"  [PASS] {fn_name}")
            passed += 1
        except Exception as exc:
            print(f"  [FAIL] {fn_name}: {exc}")
            traceback.print_exc()
            failed += 1

    return passed, failed


def main():
    print("=" * 65)
    print("AI CODE REVIEW & SECURITY ANALYSIS AGENT - TEST SUITE RUNNER")
    print("=" * 65)

    modules = [
        (t_lang, "tests/test_language_detector.py"),
        (t_code, "tests/test_code_analysis.py"),
        (t_sec, "tests/test_security_agent.py"),
        (t_rem, "tests/test_remediation.py"),
        (t_kb, "tests/test_knowledge_base.py"),
        (t_orch, "tests/test_orchestrator.py"),
        (t_routes, "tests/test_routes.py"),
    ]

    total_passed = 0
    total_failed = 0

    for mod, name in modules:
        p, f = run_module_tests(mod, name)
        total_passed += p
        total_failed += f

    print("\n" + "=" * 65)
    print(f"TEST EXECUTION SUMMARY: {total_passed} Passed, {total_failed} Failed")
    print("=" * 65)

    if total_failed > 0:
        sys.exit(1)
    else:
        print("[SUCCESS] All tests passed cleanly!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

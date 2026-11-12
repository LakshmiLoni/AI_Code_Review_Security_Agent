# Python Code Quality, Readability, and Anti-Patterns

## 1. Overview
High-quality code minimizes bugs, reduces cognitive load, improves maintainability, and prevents subtle security regressions. Adhering to Python standard conventions (PEP 8, PEP 257) ensures uniform codebase structure.

## 2. Common Code Smells in Python
- **Overly Long Functions**: Functions exceeding 40-50 lines usually violate the Single Responsibility Principle.
- **Deep Nesting**: Nesting conditional statements deeper than 3 levels impairs readability and increases cyclomatic complexity.
- **Bare Except Clauses**: Catching all exceptions with `except:` masks syntax errors, system exits, and memory errors.
- **Mutable Default Arguments**: Using `def append_to(item, target=[])` causes state to persist across function calls.
- **Wildcard Imports**: `from module import *` pollutes namespace and obscures variable origin.
- **Dead / Unused Code**: Unreferenced variables, imports, and functions add unnecessary clutter.

## 3. Refactoring Code Smells

### A. Mutable Default Argument Fix
```python
# CODE SMELL: Mutable list as default argument
def add_entry(entry: str, log: list = []):
    log.append(entry)
    return log

# CLEAN REFACTOR: Use None sentinel value
from typing import Optional, List

def add_entry_clean(entry: str, log: Optional[List[str]] = None) -> List[str]:
    if log is None:
        log = []
    log.append(entry)
    return log
```

### B. Guard Clauses to Reduce Nesting
```python
# CODE SMELL: Excessive nesting
def process_order(order):
    if order is not None:
        if order.is_paid:
            if order.items:
                if not order.is_shipped:
                    order.ship()
                    return "Shipped"

# CLEAN REFACTOR: Inverted guard clauses (Bouncer pattern)
def process_order_clean(order):
    if order is None:
        return "Invalid order"
    if not order.is_paid:
        return "Order unpaid"
    if not order.items:
        return "Empty order"
    if order.is_shipped:
        return "Already shipped"

    order.ship()
    return "Shipped"
```

## 4. Key Metrics
- Keep Cyclomatic Complexity under 10 per function.
- Enforce type hints (typing module) and run mypy in CI pipelines.
- Automate style enforcement with ruff, flake8, and black.

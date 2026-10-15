# Code Smells, Maintainability and Common Programming Mistakes

## Definition
A **code smell** is a surface symptom in code that often (not always) indicates a deeper design problem. Smells are not bugs and the code may work, but they make it harder to read, test, change and secure. Martin Fowler coined the idea; Refactoring catalogues describe the standard smells and fixes.

## Why it matters for security
Complex, duplicated, poorly tested code hides vulnerabilities. A fix applied in one of five copy-pasted blocks leaves four vulnerable. Maintainability work and security work reinforce each other.

## Common smells and fixes
| Smell | Symptom | Typical fix |
|-------|---------|-------------|
| Long method / function | Dozens of lines doing many things | Extract smaller, well-named functions |
| Large class ("God class") | One class with many responsibilities | Split by responsibility (single responsibility principle) |
| Duplicated code | Same logic copy-pasted | Extract a shared function/class |
| Deep nesting | Many nested `if`/`for` levels | Guard clauses / early returns, extract functions |
| Long parameter list | Five or more parameters | Group into an object / dataclass |
| Magic numbers and strings | Unexplained literals (`if status == 3`) | Named constants or enums |
| Dead code | Unused variables, functions, imports | Delete it (version control remembers) |
| Poor naming | `x`, `tmp`, `data2` | Intention-revealing names |
| Commented-out code | Old code kept as comments | Remove it |
| Primitive obsession | Strings/ints for domain concepts | Small value types |

## Common programming mistakes
### Python
```python
def add_item(item, items=[]):        # MISTAKE: mutable default argument is shared between calls
    items.append(item)
    return items

try:
    risky()
except:                               # MISTAKE: bare except hides errors (and catches KeyboardInterrupt)
    pass

if x == None:                         # style: use "is None"
    ...
```
Fix: `def add_item(item, items=None): items = [] if items is None else items`, catch specific exceptions and log them, use `is None`.

### Java
```java
if (name == "admin") { ... }          // MISTAKE: compares references; use "admin".equals(name)
catch (Exception e) { }               // MISTAKE: swallowed exception
public static List<String> cache;     // MISTAKE: public mutable static state
Connection c = ds.getConnection();    // MISTAKE: resource not closed -> use try-with-resources
```

### Language-independent
Off-by-one errors, unchecked null/None values, ignoring return values, catching overly broad exceptions, unclear error handling, global mutable state, missing tests for edge cases, and unused imports/variables.

## Maintainability practices
1. Follow the language style guide (PEP 8 for Python; Oracle/Google style for Java) and enforce it with linters (flake8/ruff/pylint; Checkstyle/SpotBugs).
2. Keep functions short and focused; prefer clear names over comments.
3. Write unit tests for logic and edge cases; refactor only with tests in place.
4. Document public interfaces (docstrings / Javadoc), not every line.
5. Measure complexity (cyclomatic complexity) and review hotspots first.

## Sources
- https://martinfowler.com/bliki/CodeSmell.html
- https://refactoring.guru/refactoring/smells
- https://peps.python.org/pep-0008/
- https://docs.python.org/3/faq/programming.html
- https://www.oracle.com/java/technologies/javase/codeconventions-contents.html

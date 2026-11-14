---
paths:
  - "**/*Test.java"
  - "**/*Tests.java"
---

# Testing

## One test class per production class

- A production class has one test class named after it (`Item` -> `ItemTest`, `Site` -> `SiteTest`), not a class per method or per sub-feature.
- Split a test class only when it grows large; the default is one-to-one.
- A test class is single-responsibility: it exercises exactly one production class. Do not drive several production classes from one test class, so a failure points at one unit.

## Test your own code, not the library

- Test the behavior your code adds, not behavior a framework or library already guarantees. Do not assert what Jackson, the JDK, or another dependency does on its own (serialization round-trips, collection semantics, parsing); such tests bloat the suite, re-test someone else's code, and break on a library upgrade with no bug of yours.
- Assert a library's result only where your own logic depends on it, at that boundary, not the library's general behavior.

## File layout: the TDL split

- Split a test class with a `// TDL` banner line: `@Test` methods above it, builders and helper utilities below it. A reader scans the behavior first and drops into the scaffolding only when needed.

## Naming

- Name a variable holding an id in its serialized string form with an `...AsString` suffix; the typed id is the plain name. For example `String itemIdAsString` versus `ItemId itemId`. Do not add a `Ref` suffix.
- Factor repeated setup into a named builder that reads at the call site (`newItemInSite(...)`), rather than inline construction copied across tests.
- Declare a local close to its first use, not in a block at the top of the test.
- For fixture ids and keys, prefer abstract numbered names over semantic ones (see the test-fixture-naming rule in coding-general).

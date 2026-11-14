---
paths:
  - "**/*Test.java"
  - "**/*Tests.java"
---

# Testing

## One test class per production class

- A production class has one test class named after it (`Item` -> `ItemTest`, `Site` -> `SiteTest`), not a class per method or per sub-feature.
- Split a test class only when it grows large; the default is one-to-one.

## File layout: the TDL split

- Split a test class with a `// TDL` banner line: `@Test` methods above it, builders and helper utilities below it. A reader scans the behavior first and drops into the scaffolding only when needed.

## Naming

- Name a variable holding an id in its serialized string form with an `...AsString` suffix; the typed id is the plain name. For example `String itemIdAsString` versus `ItemId itemId`. Do not add a `Ref` suffix.
- Factor repeated setup into a named builder that reads at the call site (`newItemInSite(...)`), rather than inline construction copied across tests.
- Declare a local close to its first use, not in a block at the top of the test.
- For fixture ids and keys, prefer abstract numbered names over semantic ones (see the test-fixture-naming rule in coding-general).

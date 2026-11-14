---
paths:
  - "**/*.java"
---

# Java

## Lombok over hand-written boilerplate

- If a class needs getters, setters, equals/hashCode, a logger, or a constructor, use the annotation (`@Getter`, `@Setter`, `@EqualsAndHashCode`, `@Slf4j`, `@AllArgsConstructor`, `@RequiredArgsConstructor`, `@NoArgsConstructor`) rather than hand-writing it. Never hand-write a getter that `@Getter` on the field would emit; a hand-written constructor is justified only when it derives computed fields from its inputs.
- Do not use `@Data`, `@Value`, or `@Builder`. Compose the specific annotations above instead, so a reader sees exactly what is generated. The catch-all annotations hide that and pull in behavior (a builder, forced immutability, a generated `toString`) the code does not want.
- Do not rely on `@ToString`. Its `ClassName(field=value)` form breaks any consumer that needs the bare value (string interpolation, a path canonical form). When `toString()` must return a specific value, hand-write it; otherwise leave it off.

## Imperative over streams and Optional

This is the general "prefer imperative over functional-chain style" rule (see coding-general) applied to Java.

- Prefer `if` / `for` / `while` to a `stream().filter().map().collect()` chain and to `Optional` fluent chains.
- Return `null`, not `Optional<>`, and null-check it with an explicit `if`. An `Optional.orElseThrow(...)` or `orElseGet(...)` with a non-trivial body becomes an `if` with an early return or throw.

## Error handling

- Fail fast: when an input or state is wrong, throw, do not swallow it, log-and-continue, or return a silent default.
- Throw an unchecked exception. Wrap a caught checked exception in a `RuntimeException` (or a domain subtype where one exists) and always pass the cause: `throw new RuntimeException(message, e)`. Never drop `e`.
- The message names what failed and the offending value, so the stack trace is self-explanatory: `"unknown renderer: " + key`, not `"invalid input"`.

## Collections: return unmodifiable

- A getter that exposes an internal collection returns an unmodifiable view (`Collections.unmodifiableList(...)` / `List.copyOf(...)`), so a caller cannot mutate internal state through it. This is a sanctioned exception to the Lombok-getter rule: hand-write (or `@Getter(AccessLevel)` plus a wrapper) when the field is a mutable collection.

## One class per file

- One top-level type per file. Do not nest a `private static class` or a helper `enum` inside another class.
- An `enum` or a `record` is a type in its own right: give it its own file, named after it.

## Empty blocks

- Every intentionally-empty block carries a marker comment so a reader knows the emptiness is deliberate, not an unfinished edit: a method or override body, a constructor, an empty class, interface, or record body.
- Use `// no instances` for a private no-arg constructor that exists only to block instantiation of a static utility class; use `// empty` for every other intentionally-empty block.
- Exempt: inline braces that are not blocks, such as an array initializer (`int[] xArray = {}`).

## Separators between members

- Separate members with a full-width comment rule: a line of `//` followed by 80 dashes (`// --------...`), on its own line at the member's indentation.

## Imports

- Order: `java`, `javax`, `org`, `com`, then lombok and logging. No wildcard (`.*`) imports; list each type explicitly.

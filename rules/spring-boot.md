---
paths:
  - "**/*.java"
  - "**/application*.properties"
  - "**/application*.yml"
---

# Spring Boot

Applies to Spring Boot services, on top of the Java rules.

## Controllers

- Put `@Validated` on every controller class.
- Validate every input. Request DTOs carry Bean Validation annotations (`@NotNull`, `@NotBlank`, `@Min`, `@Max`, `@Size`); a required field is never left unvalidated.
- Bind GET and list parameters to a request bean that carries those annotations, not to loose `@RequestParam` arguments.
- One controller per concern. When logic grows beyond plain CRUD, give it its own controller and service. Lookup logic that several services share goes into its own `@Service`.
- Map entities to responses in static `<Entity>ResponseMapper` classes in a `util` package: a private constructor and `public static toResponse(Entity)` methods only.

## OpenAPI documentation

- No `@Tag`, `@Operation`, `@Parameter` or `@ApiResponse` on controllers. The documentation lives in `.properties` files that a runtime customizer applies.
- This is an unusual choice: the next time a project needs OpenAPI documentation, raise it with the user before applying it.

## Errors and configuration

- One `@RestControllerAdvice` translates exceptions to HTTP responses. Map an exception only where the translation is clear and intentional; a catch-all for `IllegalArgumentException` or `IllegalStateException` turns bugs into 4xx answers.
- Log a 4xx at WARN without a stack trace, and a 5xx at ERROR with it.
- Fail fast on missing configuration: an absent required property stops startup with a message naming it, never a silent default.

## DTOs and entities

- Every endpoint takes and returns typed DTOs with explicit fields (see "Typed API contracts" in the architecture rules).
- Name a DTO entity first: `ThingCreateRequest`, not `CreateThingRequest`. DTOs shared across resources go in a `dto.commons` package.
- An immutable response DTO uses `@Getter` and `@AllArgsConstructor`.
- When create and update set the same fields, they share one population method.
- Group entity fields under section comments: `// Id` first, then the domain fields, then `// Relationships` last.

## Services

- An upsert returns a result exposing `entity()` and `wasCreated()`. The controller answers `201 Created` when `wasCreated()` is true and `200 OK` otherwise.

## Paths and filters

- Endpoints live under `/api/<resource>`, with the resource as a kebab-case plural noun (`/api/basic-events`).
- Servlet filters skip non-API paths (`/actuator`, `/swagger`, `/v3/api-docs`) in `shouldNotFilter`. Metrics interceptors skip the same paths.

## Persistence

- Cursor pagination: fetch N+1 rows; the extra row means there is a next page. Encode the cursor in an HMAC-signed token and return `PageResponse<T>(items, nextToken)`.
- Initialize lazy collections with `Hibernate.initialize()` inside a `@Transactional(readOnly = true)` method, before the data leaves it.

## Jackson

- Defaults: pretty print, properties sorted alphabetically, non-null inclusion only, ISO-8601 dates.

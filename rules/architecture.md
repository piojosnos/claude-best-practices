# Architecture

Language-agnostic design rules for services and multi-module systems.

## YAGNI

- Build what is needed now. Cross-cutting features (authentication and authorization, metrics, scheduling) come when a requirement asks for them.
- Prefer the straightforward solution to a clever abstraction. Optimize for speed of iteration and ease of understanding, not ceremony.

## A shared module for shared behavior

- When several implementations share behavior (orchestration, retry, logging, utilities), extract it into a dedicated module. Adding an implementation then means writing only its own logic.
- Create the shared module when the second implementation needs it, or when the first grows complex enough to benefit from the split; not before.

## Idempotent operations

- A load, import or other repeatable operation can be rerun after a fix with the same result and no duplicates.
- Enforce it where the data lands (an upsert keyed on a natural identifier), not by trusting callers never to repeat.

## Retry at the transport layer

- Retry transient failures (5xx, 429 Too Many Requests, timeouts) with exponential backoff and a cap on attempts. Fail any other 4xx at once; it will not succeed on a retry.
- Wire retry into the transport (an HTTP client interceptor, for example), so callers never deal with it.

## Typed API contracts

- Every endpoint takes and returns typed request and response objects with explicit fields. Use an untyped map or dictionary only when the shape is genuinely dynamic.

## Data ownership

- Each service owns its database: its own instance or schema, user and credentials. Services never share a database; they talk through their APIs.

## Containers

- Package each service as a container image. Run a multi-container setup with Docker Compose.

## Logging levels

- ERROR: a failure. WARN: something skipped or degraded. INFO: progress. DEBUG: detail.
- Log through the language's standard facility (SLF4J in Java, `logging` in Python), with enough context in the message to find the record or file involved.

## One name per service

- A service uses one short name everywhere: folder, module, container, Compose service, application name, config keys, dashboards and metric tags. Grepping that one word then finds every piece of it.

## Test data isolation

- When tests write to shared, real infrastructure, keep their data apart (for example a dedicated namespace or a prefix such as `integ-test-`) and clean it up after the run.
- Use with care: a namespace scheme reaches into the data model. Discuss it with the user before introducing one.

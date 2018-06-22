# Capture User Context

Timber automatically captures [user context](/concepts/log-event-json-schema/context/user-context) using our [Python Libary](https://github.com/timberio/timber-python#context). If you aren't sure what context is, please read the ["Metdata, Context, and Events" doc](/concepts/metadata-context-and-events). The [How it works](#how-it-works) section below also expands on this concept.

By default, all `TimberHandler` instances use the same context object (`timber.context`), but if you'd like to use multiple loggers/handlers, each with a different context, it is possible to explicitly create and pass your own by following the instructions below.


## How to use it

```python
with timber.context(job={'id': 123}):
  logger.info('Background job execution started')
  # ... code here
  logger.info('Background job execution completed')
```

Contexts nest and merge naturally:

```python
with timber.context(job={'id': 123, 'count': 1}):
  # Sends a context {'job': {'id': 123, 'count': 1}}
  logger.info('Background job execution started')
  # ... code here
  with timber.context(job={'count': 2}):
    # Sends a context {'job': {'id': 123, 'count': 2}}
    logger.info('Background job in progress')
  # ... code here
  # Sends a context {'job': {'id': 123, 'count': 1}}
  logger.info('Background job execution completed')
```

1. [Search it](/app/console/searching) with queries like: `build.version:1.0.0`
2. [View this context when viewing a log's metadata](/app/console/view-metdata-and-context)


## How it works

Context represents the current environment when the log was written. It's extremely powerful and introduces a missing gap with standard Python logging. In essence, its joins data for your logs, allowing you tor relate logs together without complicated regex searches. It's how Timber is able to provide features like [tailing a user](/app/console/tail-a-user) and [tracing a request](/app/console/trace-http-requests).

When your logs are received by the Timber service, they'll have the context included. The resulting JSON document for an example log will look like:

```json
{
  "message": "My log message",
  "level": "info",
  "context": {
    "custom": {
      "job": {
        "id": 123,
      }
    }
  }
}
```

---

### Related Docs

1. [**Metadata, context, and events**](/timber-concepts/metadata-context-and-events)
2. [**Your application's dynamic schema**](/timber-concepts/application-schema)
3. [**Service Limits**](/timber-concepts/service-limits)
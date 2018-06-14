# Basic Logging

Use the [`Timber::Logger`](https://github.com/timberio/timber-python) just like you would the standard Python [`::Logger`](https://docs.python.org/3/library/logging.html).


## How to use it

```python
logger.debug("Debug message")
logger.info("Info message")
logger.warn("Warn message")
logger.error("Error message")
logger.fatal("Fatal message")
```

## Changing the Log Level

Adjusting the log level in Python is not specfic to `TimberHandler`, like any other `logger.Handler`.

```python
# Only respond to events as least as important as `warning`
timber_handler = timber.TimberHandler(api_key='...', level=logging.WARNING)
```

We encourage standard / traditional log messages for non-meaningful events. And because Timber [_augments_](/timber-concepts/structuring-through-augmentation) your logs with metadata, you don't have to worry about making every log structured!

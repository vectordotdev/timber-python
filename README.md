# Timber - Master your Python app with structured logging

Timber for Python is a `logging` handler that sends your log statements to [Timber](https://timber.io), making them [easier to search, use, and read](https://github.com/timberio/timber-ruby#get-things-done-with-your-logs). In particular, `timber` makes it easier to add [metadata and context](https://timber.io/docs/concepts/metadata-context-and-events) to your log statements.

:point_right: **Timber python is under development and is in beta testing, if interested in joining, please email us at [beta@timber.io](mailto:beta@timber.io)**

# Installation

To install the library and get started logging to Timber:

```bash
pip install timber
```

# Usage

### Basic Logging

`timber` provides a `TimberHandler` that works with the built-in `logging` library. Just like any other handler,
all that you need to do to set it up is add it to a logger:

```python
import logging
import timber

logger = logging.getLogger(__name__)

timber_handler = timber.TimberHandler(api_key='...')
logger.addHandler(timber_handler)
```

Then, make logging calls just like usual:

```python
logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.critical('Critical message')
logger.error('Error message')
```

### Logging Events (structured data)

Log structured data by providing named events as part of the `extra` parameter to any logging call:

```python
logger.debug('Debug message', extra={
  'payment_rejected': {
    'customer_id': 'abcd1234',
    'amount': 1000,
    'reason': 'Card Expired',
  }
})
```

Any top-level `dict` on the `extra` argument will be sent as an event to the Timber console. All other types will be ignored.

### Setting Context

Add shared structured data across multiple logging statements:

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

# Configuration

The `TimberHandler` takes a variety of parameters that allow for fine-grained control over its behavior.

### `level`
Like any other `logger.Handler`, the `TimberHandler` can be configured to only respond to log events of a specific level:

```python
# Only respond to events as least as important as `warning`
timber_handler = timber.TimberHandler(api_key='...', level=logging.WARNING)
```

### `buffer_capacity` and `flush_interval`
Timber buffers log events and sends them in the background for maximum performance. All outstanding log events are sent when the buffer is full or a certain amount of time has passed since any events were sent. To control the size of the buffer, pass the `buffer_capacity` argument:

```python
# Never allow more than 50 outstanding log events
timber_handler = timber.TimberHandler(api_key='...', buffer_capacity=50)
```

To control the maximum amount of time between buffer flushes, pass the `flush_interval` argument:

```python
# Send any outstanding log events at most every 60 seconds
timber_handler = timber.TimberHandler(api_key='...', flush_interval=60)
```

### `raise_exceptions`
Logging should never break your application, which is why the `TimberHandler` suppresses all internal exceptions by default. To change this behavior:

```python
# Allow exceptions from internal log handling to propagate to the application,
# instead of suppressing them.
timber_handler = timber.TimberHandler(api_key='...', raise_exceptions=True)
```

### `drop_extra_events`
As soon as the internal log event buffer is full, Timber flushes all of the events to the server, but while that occurs any incoming log events are dropped by default. To make your application block in this case to ensure that all log statements are sent to Timber:

```python
# Make log statements block until the internal log event buffer is no longer full.
timber_handler = timber.TimberHandler(api_key='...', drop_extra_events=False)
```

### `context`
By default all `TimberHandler` instances use the same context object (`timber.context`), but if you'd like
to use multiple loggers and multiple handlers, each with a different context, it is possible to explicitly
create and pass your own:

```python
import logging
import timber

logger = logging.getLogger(__name__)

context = timber.TimberContext()
timber_handler = timber.TimberHandler(api_key='...', context=context)
logger.addHandler(timber_handler)

with context(job={'id': 123}):
  logger.critical('Background job execution started')
  # ... code here
  logger.critical('Background job execution completed')
```

# Testing

1. Install the packages required for development and testing:

```bash
pip install -r requirements.txt
pip install -r test-requirements.txt
```

2. Run the tests:

```bash
nosetests
```

To see test coverage, run the following and then open `./htmlcov/index.html` in your browser:

```bash
nosetests --with-coverage --cover-branches --cover-package=timber tests
coverage html --include='timber*'
```

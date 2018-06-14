# Buffer Capacity and Flush Interval

Timber buffers log events and sends them in the background for maximum performance. All outstanding log events are sent when the buffer is full or a certain amount of time has passed since any events were sent. To control the size of the buffer, pass the `buffer_capacity` argument:

```python
# Never allow more than 50 outstanding log events
timber_handler = timber.TimberHandler(api_key='...', buffer_capacity=50)
```

To control the maximum amount of time between buffer flushes, pass the flush_interval argument:

```python
# Send any outstanding log events at most every 60 seconds
timber_handler = timber.TimberHandler(api_key='...', flush_interval=60)
```

## Drop Extra Events

As soon as the internal log event buffer is full, Timber flushes all of the events to the server, but while that occurs any incoming log events are dropped by default. To make your application block in this case to ensure that all log statements are sent to Timber:

```python
# Make log statements block until the internal log event buffer is no longer full.
timber_handler = timber.TimberHandler(api_key='...', drop_extra_events=False)
```
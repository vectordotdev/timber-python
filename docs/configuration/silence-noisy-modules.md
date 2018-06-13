# Silence Noisy Modules

By default, some modules (like `requests`) write log messages to the console. It's easy to silence these messages.

```python
logging.getLogger("requests").setLevel(logging.WARNING)
```

This instructs the `requests` module to only log messages if they are at least `warning`.
# Raise Exceptions

Logging should never break your application, which is why the `TimberHandler` suppresses all internal exceptions by default. To change this behavior:

```python
# Allow exceptions from internal log handling to propagate to the application,
# instead of suppressing them.
timber_handler = timber.TimberHandler(api_key='...', raise_exceptions=True)
```
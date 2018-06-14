# Custom Events

Custom events allow you to extend beyond events already defined in
the [`Timber::Events`](https://github.com/timberio/timber-python#logging-events-structured-data) namespace. If you aren't sure what an event is, please read the ["Metdata, Context, and Events" doc](/concepts/metadata-context-and-events).


## How to use it

```python
logger.debug('Debug message', extra={
  'payment_rejected': {
    'customer_id': 'abcd1234',
    'amount': 1000,
    'reason': 'Card Expired',
  }
}) 
```

1. [Search it](/app/console/searching) with queries like: `type:payment_rejected` or `payment_rejected.amount:>100`
2. [Alert on it](/app/alerts) with threshold based alerts
3. [Graph & visualize it](/app/graphs)
4. [View this event's data and context](/app/console/view-metadata-and-context)


## How it works

When this event is received by the Timber service we'll define a namespaced schema based on the event name. In this case, the namespace would be `payment_rejected`. The data structure of your log will look like:

```json
{
  "message": "Payment rejected",
  "level": "warn",
  "event": {
    "custom": {
      "payment_rejected": {
        "customer_id": "abcd1234",
        "amount": 100,
        "reason": "Card expired"
      }
    }
  }
}
```

---

### Related Docs

1. [**When to use custom events?**](/timber-guides/when-to-use-custom-events)
2. [**Metadata, context, and events**](/timber-concepts/metadata-context-and-events)
3. [**Your application's dynamic schema**](/timber-concepts/application-schema)
4. [**Service Limits**](/timber-concepts/service-limits)

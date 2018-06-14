# Python Installation

1. In your shell, *run*: <small style="float: right" class="platform-alt"><a href="/platforms">prefer to integrate with your platform instead?</a></small>

```shell
pip install timber
```

*In your entry file:*
```python
import logging
import timber

logger = logging.getLogger(__name__)

timber_handler = timber.TimberHandler(api_key='...')
logger.addHandler(timber_handler)
```

Continue to make logging calls like normal.

---

### Related docs

1. [**Obtaining your API key**](/app/applications/obtaining-your-api-key)
2. [**Troubleshooting**](/languages/python/troubleshooting)
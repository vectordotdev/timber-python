---
description: Learn how to set up Timber on Python.
related:
- /app/applications/obtaining-your-api-key
- /languages/python/troubleshooting
---
1. In your shell, *run*: <small style="float: right" class="platform-alt"><a href="/platforms">prefer to integrate with your platform instead?</a></small>

  ```shell
  pip install timber
  ```

2. In your entry file:

  ```python
  import logging
  import timber

  logger = logging.getLogger(__name__)

  timber_handler = timber.TimberHandler(api_key='...')
  logger.addHandler(timber_handler)
  ```

3. Continue to make logging calls like normal.

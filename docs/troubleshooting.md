---
description: We're here to help if you're having issues.
---
# Python Troubleshooting

*If you're having trouble don't hesitate to [contact us](mailto:support@timber.io)! We're passionate about helping our customers and providing good user experiences.*

![This is fine](//images.contentful.com/h6vh38q7qvzk/1R4u3xGgok8KICOAgoIGEI/655e36643ecd5bd28c51aec8762786fc/post-64231-this-is-fine-dog-fire-comic-Im-N7mp.png)

If you are here, it's likely you're having trouble sending logs from your application to Timber. Not to worry! This document will help you identify the root cause. To use your time as efficiently as possible here are the steps you should take:

## 1. Rule out Timber service issues by testing delivery

The very first thing you should do is rule out that Timber is not the cause by sending a simple test log to your Timber application. First, try it locally. If that works, try it on your application's server. The latter being the most important.

```shell
curl -X POST https://logs.timber.io/frames \
  -H 'authorization: Basic base64_encode({{my-timber-api-key}})' \
  -H 'content-type: text/plain' \
  -d 'Test log line to test delivery'
  -v
```

Be sure to base 64 encode your API key. Here's an example with Ruby.

```shell
irb
```

Then paste in:

```ruby
require "base64"
Base64.urlsafe_encode64("{{my-timber-api-key}}")
````

On average log lines will appear within 5 seconds of delivery but in some cases can take up to 20 seconds depending on network latency, etc.


## 2. Enable debug logging within the Timber library

Timber comes packaged with debugging options, this will give you access to the internal debug logs that the Timber library produces. Enabling them is easy:

```python
# Allow exceptions from internal log handling to propagate to the application,
# instead of suppressing them.
timber_handler = timber.TimberHandler(api_key='...', raise_exceptions=True)
```

### What to do with the logs?

Look for the term `Exception`. Specficially, you should see your stack and your error message.

If you do not see any errors, your application should be delivering logs appropriately.

## What if none of this resolved my issue?

[Contact us](mailto:support@timber.io). We're passionate about helping customers, we'll do our best to find the root cause.

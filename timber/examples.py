# l.critical('hello')
{
  "threadName": "MainThread",
  "name": "root",
  "thread": 140735249956864,
  "created": 1525878342.825053,
  "process": 9190,
  "processName": "MainProcess",
  "args": [],
  "module": "<ipython-input-13-69ef70fd97ca>",
  "filename": "<ipython-input-13-69ef70fd97ca>",
  "levelno": 50,
  "exc_text": None,
  "pathname": "<ipython-input-13-69ef70fd97ca>",
  "lineno": 1,
  "msg": "hello",
  "exc_info": None,
  "funcName": "<module>",
  "relativeCreated": 45135.591983795166,
  "levelname": "CRITICAL",
  "msecs": 825.0529766082764
}
# l.critical('hello %s', 'world', extra={'user.name': 'peter'})
{
  "threadName": "MainThread",
  "name": "root",
  "thread": 140735249956864,
  "created": 1525878542.121747,
  "process": 9190,
  "user.name": "peter",
  "processName": "MainProcess",
  "args": [
    "world"
  ],
  "module": "<ipython-input-16-f279f34502d0>",
  "filename": "<ipython-input-16-f279f34502d0>",
  "levelno": 50,
  "exc_text": None,
  "pathname": "<ipython-input-16-f279f34502d0>",
  "lineno": 1,
  "msg": "hello %s",
  "exc_info": None,
  "funcName": "<module>",
  "relativeCreated": 244432.28602409363,
  "levelname": "CRITICAL",
  "msecs": 121.74701690673828
}

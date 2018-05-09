import time
import timber
import logging

api_key = '2884_4ca58cdc23d5d4cb:94e6649c9916ab5f2bf9afdaa14ef5f4b1fd254b1114fac7a1480979e65686c6'

logger = logging.getLogger()
formatter = logging.Formatter('%(age)s %(username)s: %(message)s')
logger.formatter = formatter
clogger = timber.ContextLogger(logger, api_key)

T = time.time()
with clogger.context('user', {'name': 'peter', 'age': 24}):
    clogger.critical('inside first context')
    with clogger.context('user', {'name': 'paul'}):
        clogger.critical('second context', extra={'foo': 'bar'})
#clogger.critical('last step %d', T)

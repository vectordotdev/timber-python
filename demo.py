import time
import timber
import logging
import sys

api_key = '2884_4ca58cdc23d5d4cb:94e6649c9916ab5f2bf9afdaa14ef5f4b1fd254b1114fac7a1480979e65686c6'

logger = logging.getLogger()
# Add a handler that prints to STDOUT
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
logger.addHandler(stdout_handler)
# Add the Timber handler
timber_handler = timber.TimberHandler(
    api_key,
    buffer_capacity=10,
    flush_interval=2,
    level=logging.DEBUG
)
logger.addHandler(timber_handler)


with timber.context(user={'name': 'peter', 'age': 24}):
    # This won't be shown, as both the STDOUT handler and the Timber handler
    # require events to be of level >= DEBUG.
    logging.info('hello again')
    # This will be shown.
    logger.critical('inside first context')

    with timber.context(user={'name': 'paul'}, additional={'age': 100}):
        # This `extra` is not sent to Timber because it is not a `dict`. No
        # custom event will be created.
        logger.warning('second context', extra={'foo': 'bar'})

    # This `extra` IS sent to Timber because it is a `dict`.This will create a
    # custom 'payment_rejected' event.
    logger.error('back to the first context, inside an event',
                 extra={'payment_rejected': {'customer_id': 'abcd123',
                                             'amount': 100,
                                             'reason': 'Card expired'}})

    # This is necessary to make sure that the log buffer is flushed.
    print('>>> about to sleep to flush events')
    time.sleep(timber_handler.flush_interval + 1)
    print('>>> done')

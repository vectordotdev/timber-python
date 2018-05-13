import time
import timber
import logging

api_key = '2884_4ca58cdc23d5d4cb:94e6649c9916ab5f2bf9afdaa14ef5f4b1fd254b1114fac7a1480979e65686c6'

logger = logging.getLogger()
handler = timber.TimberHandler(api_key, level=logging.DEBUG)
logger.addHandler(handler)


with timber.context(user={'name': 'peter', 'age': 24}):
    logger.critical('inside first context')

    handler.setFormatter(logging.Formatter('%(message)s [%(foo)s]'))
    with timber.context(user={'name': 'paul'}, additional={'age': 100}):
        logger.critical('second context', extra={'foo': 'bar'})
    handler.setFormatter(logging.Formatter('%(message)s'))


    payment_event = {
        'customer_id': 'abcd123',
        'amount': 100,
        'reason': 'Card expired',
    }
    with timber.event(payment_rejected=payment_event):
        logger.critical('back to the first context, inside an event')

    logger.debug('done')

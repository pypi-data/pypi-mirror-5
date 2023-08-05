XMPPHandler for Python logging
------------------------------

Usage example, assumes gmail.com account.

::

    from xmpp_logging_handler import XMPPHandler
    import logging
    logger = logging.getLogger()
    myHandler = XMPPHandler('SENDING_USER', 'SENDING_PASSWORD', ['raymond@thisislevelup.com',],)
    logger.addHandler(myHandler)
    logging.error('Its broken')
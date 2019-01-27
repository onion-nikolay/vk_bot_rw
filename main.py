import logging
import os
import session
import time

if __name__ == '__main__':
    try:
        os.mkdir('data')
    except OSError:
        pass
    logger = session.new_logger()
    logger.info('Program started.')
    while 'My code sucks':
        try:
            output = session.session(logger)
            if output == -1:
                logger.info('Program stopped by admin (message).')
                logging.shutdown()
                break
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info('Program stopped by admin (console).')
            logging.shutdown()
            break
        except Exception as e:
            logger.exception(e)
            logger.info('Trying to restart.')
            continue

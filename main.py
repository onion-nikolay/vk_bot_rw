from time import sleep
import logging, os

from session import session, logger as newLogger


if __name__ == '__main__':
    try:
        os.mkdir('data')
    except:
        pass
    logger = newLogger()
    logger.info('Program started.')
    while 'My code sucks':
        try:
            output = session(logger)
            if output == -1:
                logger.info('Program stopped by admin (message).')
                logging.shutdown()
                break
            sleep(1)
        except KeyboardInterrupt:
            logger.info('Program stopped by admin (console).')
            logging.shutdown()
            break
        except Exception as e:
            logger.exception(e)
            logger.info('Trying to restart.')
            continue

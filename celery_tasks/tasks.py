import time
from celery import Celery
from celery.utils.log import get_task_logger

import logging
from pyinstrument import Profiler
from scraping import hacker_news

# Custom formatter for the log file
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Configure the logger file for storing the logs of profiler
logger = logging.getLogger('profiler_log')
logger.setLevel(logging.INFO)

# Create a file handler and set the formatter
log_file = 'worker.log'
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(log_formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

logger = get_task_logger(__name__)

app = Celery('tasks',
             broker='amqp://admin:mypass@rabbit:5672',
             backend='rpc://')


@app.task(default_retry_delay=10)
def longtime_add():
    """
    profile -> app profiler to measure the performance of function
    this function will execute the scrapper and will store the data in .db file.
    """
    profiler = Profiler()
    profiler.start()

    logger.info('Got Request - Starting work ')
    time.sleep(4)

    hacker_news.start_scrap_data()

    logger.info('Work Finished ')
    profiler.stop()

    logger.info(profiler.output_text(unicode=True, color=True))

    return True

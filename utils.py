import os
import logging
import time
from functools import wraps

"""
Time wrapper from https://gist.github.com/bradmontgomery/bd6288f09a24c06746bbe54afe4b8a82
"""
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)-4s %(message)s')


time_logger = logging.getLogger(__name__)


file_handler = logging.FileHandler('logs/global.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

file_handler2 = logging.FileHandler('logs/global_debug.log')
file_handler2.setLevel(logging.DEBUG)
file_handler2.setFormatter(formatter)

file_handler_time = logging.FileHandler('logs/execution_time.log')
file_handler_time.setFormatter(formatter)
file_handler_time.setLevel(logging.WARNING)


stream_handler = logging.StreamHandler()
stream_handler_formatter = logging.Formatter('[%(levelname)s] %(message)s')
stream_handler.setFormatter(stream_handler_formatter)
stream_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.addHandler(file_handler2)

time_logger.addHandler(stream_handler)
time_logger.addHandler(file_handler_time)


def log(log_type,string):

    if log_type=="AUTHORING ERROR" or log_type=="FATAL ERROR":
        logger.error(string)
    elif log_type == 'ERROR':
        logger.error(string)
    elif log_type == 'DEBUG':
        logger.debug(string)
    elif log_type == "INFO":
        logger.info(string)
    elif log_type == "TIME TOOK":
        logger.debug(string)
        time_logger.warning(string)
    else:
        logger.debug(string)

def timed(func):
    """This decorator prints the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        file_path = func.__code__.co_filename # extract the path of the function 
        k = file_path.rfind("/")
        file_name = file_path[k+1:] #take the latest / of the path (may cause error if running on windows )
        
        log('TIME TOOK',"Time took for function {} in file {} is {} s".format(func.__name__,file_name, round(end - start, 2)))
        return result

    return wrapper


if __name__ == "__main__":
    log("AUTHORING ERROR",'@Thierry Lincoln Test')



"""
import slack
import asyncio
import tracemalloc
tracemalloc.start()

#SLACK_API_DEBUG_TOKEN = os.getenv("SLACK_API_DEBUG_TOKEN")
#client = slack.WebClient(token=SLACK_API_DEBUG_TOKEN,run_async=True)
#loop = asyncio.get_event_loop()
#loop.run_until_complete(post_slack_message(string))


async def post_slack_message(text):
    response = await client.chat_postMessage(
                        channel="popbots-bugs-report",
                        text=text
                    )

"""
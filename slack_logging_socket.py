import slack
import asyncio
import tracemalloc
import time
from loggingtail import LogWatcher
import os
tracemalloc.start()

SLACK_API_DEBUG_TOKEN = os.getenv("SLACK_API_DEBUG_TOKEN")
client = slack.WebClient(token=SLACK_API_DEBUG_TOKEN,run_async=False)



def post_slack_message(text):
    response = client.chat_postMessage(
                        channel="popbots-automatic-bugs-report",
                        text=text
                    )
i = 0
last_message =""
def callback(filename, lines):
    global i
    global last_message
    i+=1
    print(f"Callback call {i}")
    lines = [str(line.decode("utf-8")) for line in lines]
    for line in lines:
        if 'ERROR' in str(line) and line != last_message:
            post_slack_message(line)
            last_message = line
            print(line)
            return True

watcher = LogWatcher("logs/", callback)
while 1:
    watcher.loop(blocking=False)
    time.sleep(0.5)

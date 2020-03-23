import os
import slack
import asyncio
import tracemalloc
tracemalloc.start()


SLACK_API_DEBUG_TOKEN = os.getenv("SLACK_API_DEBUG_TOKEN")
client = slack.WebClient(token=SLACK_API_DEBUG_TOKEN,run_async=True)
loop = asyncio.get_event_loop()


async def post_slack_message(text):
    response = await client.chat_postMessage(
                        channel="popbots-bugs-report",
                        text=text
                    )
def log(log_type,string):

    if log_type=="AUTHORING ERROR" or log_type=="FATAL ERROR":
        loop.run_until_complete(post_slack_message(string))
        
    print(f"[{log_type}] {string}")



if __name__ == "__main__":
    log("AUTHORING ERROR",'@Thierry Lincoln Test')


    
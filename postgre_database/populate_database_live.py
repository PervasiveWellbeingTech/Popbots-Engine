from live_google_sheet import fetch_csv
from bot_management import add_bot_content
from conversation import ContentFinderJoin
import psycopg2

SPREADSHEET_ID = "1mlegVF0CFDVVRgrfe08J53j6eNfHRThQitIuUEA5pwU"
RANGE_NAME = "Users"

bot_id = 6

try:
    user_table = fetch_csv(SPREADSHEET_ID,RANGE_NAME)
    active_bots = [user['name'] for index,user in user_table[user_table['active'] == '1'].iterrows() ]


except (Exception, psycopg2.DatabaseError) as error:
    print(error)

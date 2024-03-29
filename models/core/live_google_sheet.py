from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import pandas as pd


from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']
SERVICE_ACCOUNT_FILE = 'credentials/service_credentials.json'



def get_google_sheet(spreadsheet_id, range_name):
    """ Retrieve sheet data using OAuth credentials and Google Python API. """
    scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']	

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scopes)
    service = build('sheets', 'v4', credentials = creds)
    # Call the Sheets API
    gsheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    return gsheet


def gsheet2df(gsheet):
    """ Converts Google sheet data to a Pandas DataFrame.
    Note: This script assumes that your data contains a header file on the first row!
    Also note that the Google API returns 'none' from empty cells - in order for the code
    below to work, you'll need to make sure your sheet doesn't contain empty cells,
    or update the code to account for such instances.
    """
    header = gsheet.get('values', [])[0]   # Assumes first line is header!
    values = gsheet.get('values', [])[1:]  # Everything else is data.
    if not values:
        print('No data found.')
    else:
        all_data = []
        for col_id, col_name in enumerate(header):
            column_data = []
            for row in values:
                column_data.append(row[col_id])
            ds = pd.Series(data=column_data, name=col_name)
            all_data.append(ds)
        df = pd.concat(all_data, axis=1)
        return df

def fetch_csv(SPREADSHEET_ID,RANGE_NAME):

    gsheet = get_google_sheet(SPREADSHEET_ID, RANGE_NAME)
    df = gsheet2df(gsheet)

    return df


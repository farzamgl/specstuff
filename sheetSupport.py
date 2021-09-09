from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = '1YfNEdrXEHRLEvV8KjvLy8PZYHxctiLte1G5HsDPcTSU'

def addSheet(self, name):
    response = self.get(spreadsheetId=SPREADSHEET_ID, ranges=[]).execute()
    names = [item.get("properties").get("title") for item in response.get("sheets")]

    if name not in names:
      body = {
        "requests": [
          {"addSheet": {"properties": {"title": name}}}
        ]
      }
      response = self.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
      return response.get('replies')[0].get('addSheet').get('properties').get('sheetId')
    else:
      return response.get('sheets')[names.index(name)].get('properties').get('sheetId')

def writeSheet(self, range, values): 
    body = {
      "valueInputOption": "USER_ENTERED",
      "data" : {
        "range": range,
        "majorDimension": "ROWS",
        "values": values
      }
    }
    self.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()

def formatSheet(self, sheetId, rows, cols):
    body = {
      'requests': [
        {
          'autoResizeDimensions': {
            'dimensions': {
              'sheetId': sheetId,
              'dimension': 'COLUMNS',
              'startIndex': 0,
              'endIndex': cols
            }
          }
        },
        {
          'repeatCell': {
            'cell': {
              'userEnteredFormat': {
                'horizontalAlignment': 'CENTER',
                'verticalAlignment': 'MIDDLE',
              }
            },
            'range': {
              'sheetId': sheetId,
              'startRowIndex': 0,
              'endRowIndex': rows,
              'startColumnIndex': 0,
              'endColumnIndex': cols,
            },
            'fields': 'userEnteredFormat'
          }
        }
      ]
    }
    self.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()

def initSheets():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheets = service.spreadsheets()
    return sheets

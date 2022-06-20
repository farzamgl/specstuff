from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']

def addSheet(self, spreadsheetId, name):
    response = self.get(spreadsheetId=spreadsheetId, ranges=[]).execute()
    names = [item.get("properties").get("title") for item in response.get("sheets")]

    if name not in names:
      body = {
        "requests": [
          {"addSheet": {"properties": {"title": name}}}
        ]
      }
      response = self.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()
      return response.get('replies')[0].get('addSheet').get('properties').get('sheetId')
    else:
      return response.get('sheets')[names.index(name)].get('properties').get('sheetId')

def writeSheet(self, spreadsheetId, range, values): 
    body = {
      'valueInputOption': 'USER_ENTERED',
      'data' : {
        'range': range,
        'majorDimension': 'ROWS',
        'values': values
      }
    }
    self.values().batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()


def formatSheet(self, spreadsheetId, sheetId, rows, cols):
    body = {
      'requests': [
        {
          'repeatCell': {
            'cell': {
              'userEnteredFormat': {
                'numberFormat': {
                  'type': 'PERCENT',
                  'pattern': '#0.00%'
                },
                'horizontalAlignment': 'CENTER',
                'verticalAlignment': 'MIDDLE',
              }
            },
            'range': {
              'sheetId': sheetId,
              'startRowIndex': 0,
              'endRowIndex': rows,
              'startColumnIndex': 2,
              'endColumnIndex': cols,
            },
            'fields': 'userEnteredFormat'
          }
        },
        {
          'updateSheetProperties': {
            'properties': {
              'sheetId': sheetId,
              'gridProperties': {
                'frozenRowCount': 1,
                'frozenColumnCount': 1
              }
          },
          'fields': 'gridProperties.frozenRowCount, gridProperties.frozenColumnCount'
          }
        },
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
      ]
    }
    self.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()

def paintCells(self, spreadsheetId, sheetId, colStart, colEnd):
    body = {
      'requests': [
        {
          'addConditionalFormatRule': {
            'rule': {
              'ranges': {
                'sheetId': sheetId,
                'startColumnIndex': colStart,
                'endColumnIndex': colEnd,
              },
              'booleanRule': {
                'condition': {
                  'type': 'NUMBER_GREATER_THAN_EQ',
                  'values': {
                    'userEnteredValue': '0.2'
                  }
                },
                'format': {
                  'backgroundColor': {
                    'red': 0xe0/255,
                    'green': 0x66/255,
                    'blue': 0x66/255
                  }
                }
              }
            },
            'index': 0
          }
        },
        {
          'addConditionalFormatRule': {
            'rule': {
              'ranges': {
                'sheetId': sheetId,
                'startColumnIndex': colStart,
                'endColumnIndex': colEnd,
              },
              'booleanRule': {
                'condition': {
                  'type': 'NUMBER_GREATER_THAN_EQ',
                  'values': {
                    'userEnteredValue': '0.05'
                  }
                },
                'format': {
                  'backgroundColor': {
                    'red': 0xea/255,
                    'green': 0x99/255,
                    'blue': 0x99/255
                  }
                }
              }
            },
            'index': 1
          }
        },
      ]
    }
    self.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()

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

import gspread
from oauth2client.service_account import ServiceAccountCredentials


def clear_spreadsheet(name):
    # Set up credentials for Google API
    google_scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        r'C:\Users\chase\Downloads\sixth-hawk-393504-f8baa14e8c72.json', google_scope)
    client = gspread.authorize(creds)

    # Open the spreadsheet and select the worksheet
    spreadsheet = client.open(name)
    worksheet = spreadsheet.get_worksheet(0)

    # Get the number of rows in the worksheet
    num_rows = worksheet.row_count

    # Delete rows from 2 to the end
    if num_rows > 1:
        worksheet.delete_rows(2, num_rows)  # The range is inclusive

    print("Spreadsheet cleared except for the first row.")

clear_spreadsheet("userSongs")
clear_spreadsheet("playlist")

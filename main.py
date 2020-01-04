from __future__ import print_function
import pickle
import os.path
from parser import parse_order
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import email

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_creds():
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_page_ids(service, messages_list, pageToken=None):
    results = service.users().messages().list(userId='me', q='grandexam', maxResults=500, pageToken=pageToken).execute()
    messages_list.extend(results['messages'])
    nextPageToken = results.get('nextPageToken', None)
    return nextPageToken

def get_all_ids(service):
    messages_list = []
    nextPageToken = get_page_ids(service, messages_list)
    while(nextPageToken):
        nextPageToken = get_page_ids(service, messages_list, nextPageToken)
    return set([i['id'] for i in messages_list])

def data_encoder(text):
    message = None
    if len(text)>0:
        message = base64.urlsafe_b64decode(text)
        message = str(message, 'utf-8')
        message = email.message_from_string(message)
    return message


def readMessage(content)->str:
    message = None
    if "data" in content['payload']['body']:
        message = content['payload']['body']['data']
        message = data_encoder(message)
    elif "data" in content['payload']['parts'][0]['body']:
        message = content['payload']['parts'][0]['body']['data']
        message = data_encoder(message)
    else:
        print("body has no data.")
    return str(message)

def get_orders(service, ids_list):
    orders = []
    for i, id in enumerate(ids_list):
        message = service.users().messages().get(userId='me',id=id, format='full').execute()
        order_html = readMessage(message)
        if order_html:
            orders.append(order_html)
        # r = message['snippet']
        # raw = message['raw']
        # r = email.message_from_string(str(base64.urlsafe_b64decode(raw)))

        # print(order_html)

        # message = service.users().messages().get(userId='me',id=id,format='minimal')

        # pprint.pprint(message)
        # pprint.pprint(body)
        # payload = message['payload']['body']['data']
        # print(base64.b64decode(payload))
        # pprint.pprint(payload)
        # print(base64.b64decode(payload))
        if i==0:
            return [order_html]

def main():
    creds = get_creds()
    service = build('gmail', 'v1', credentials=creds)
    ids_list = get_all_ids(service)
    # TODO: отфильтровать уже обработанные сообщения
    order_html_list = get_orders(service, ids_list)
    for order in order_html_list:
        res = parse_order(order)
        print(res)
    # print(order_html_list)
    # import pprint
    # pprint.pprint(results)
    # pprint.pprint(results.__len__())



if __name__ == '__main__':
    main()
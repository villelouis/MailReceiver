from __future__ import print_function

import base64
import email
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from parser import parse_order

IDS_STORE = 'data.pickle'
TOKEN_STORE = 'token.pickle'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MESSAGES_STORE = 'messages.pickle'

def get_creds():
    if os.path.exists(TOKEN_STORE):
        with open(TOKEN_STORE, 'rb') as token:
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
        with open(TOKEN_STORE, 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_page_ids(service, messages_list, pageToken=None):
    results = service.users().messages().list(userId='me', q='grandexam@yandex.ru', maxResults=500, pageToken=pageToken).execute()
    messages_list.extend(results['messages'])
    nextPageToken = results.get('nextPageToken', None)
    return nextPageToken


def get_all_ids(service):
    messages_list = []
    nextPageToken = get_page_ids(service, messages_list)
    while (nextPageToken):
        nextPageToken = get_page_ids(service, messages_list, nextPageToken)
    return set([i['id'] for i in messages_list])


def data_encoder(text):
    message = None
    if len(text) > 0:
        message = base64.urlsafe_b64decode(text)
        message = str(message, 'utf-8')
        message = email.message_from_string(message)
    return message


def readMessage(content) -> str:
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
    processed_ids = []
    for i, id in enumerate(ids_list):
        message = service.users().messages().get(userId='me', id=id, format='full').execute()
        order_html = readMessage(message)
        try:
            order = parse_order(order_html, id)
        except:
            print(f"при обработке сообщения произошла ошибка")
            continue
        if order:
            orders.append(order)
            processed_ids.append(id)
        print(f"сообщение {i} из {len(ids_list)} обработано")
    return orders, processed_ids


def get_stored_messages():
    if os.path.exists(IDS_STORE):
        with open(IDS_STORE, 'rb') as f:
            stored_messages = pickle.load(f)
            return stored_messages
    return None


def filter_messages(message_ids: set):
    stored_messages = get_stored_messages()
    if not stored_messages:
        return message_ids
    return message_ids.difference(stored_messages)


def store_data(data, store_path):
    with open(store_path, 'wb') as f:
        pickle.dump(data, f)


def main():
    print("авторизация")
    creds = get_creds()
    service = build('gmail', 'v1', credentials=creds)

    print('получение id сообщений')
    message_ids = get_all_ids(service)
    print(f'получено сообщений {len(message_ids)}')

    print("фильтрация уже обработанных сообщений")
    filtred_message_ids = filter_messages(message_ids)
    print(f"осталось сообщений после фильтрации {len(filtred_message_ids)}")

    print("получение списка заказов и списка id обработанных сообщений")
    orders, processed_ids = get_orders(service, filtred_message_ids)
    print(f"обработано заказов {len(orders)}")

    print("запись id обработаных сообщений")
    store_data(processed_ids, IDS_STORE)

    print("запись обработанных сообщений в хранилище")
    store_data(orders, MESSAGES_STORE)


if __name__ == '__main__':
    main()

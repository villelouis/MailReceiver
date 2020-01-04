import os
from settings import MESSAGES_STORE
import pickle

def get_stored_messages():
    if os.path.exists(MESSAGES_STORE):
        with open(MESSAGES_STORE, 'rb') as f:
            stored_messages = pickle.load(f)
            return stored_messages
    return None

if __name__ == '__main__':
    import pprint
    print(len(get_stored_messages()))
    # for i, order in enumerate(get_stored_messages()):
    #     if len(order['items']) == 2:
    #         pprint.pprint(order)
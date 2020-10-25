# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

import registrationCodes

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__))

    # This registration token comes from the client FCM SDKs.
    registration_token = registrationCodes.registration_token_samsung

    cred = credentials.Certificate(path + "/fir-tutorial-2-firebase-adminsdk.json")
    default_app = firebase_admin.initialize_app(cred)

    message = messaging.Message(
        notification=messaging.Notification(
            title='Title 12',
            body='Content 12'
        ),
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                channel_id='default_channel'
            )
        ),
        token=registration_token,
    )
    response = messaging.send(message)
    print('Successfully sent message:', response)

    # Response is a message ID string.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

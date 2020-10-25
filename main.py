# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import socket
import argparse
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

import registrationCodes


def parse_arguments():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Positional mandatory arguments
    parser.add_argument("name", help="File Name", type=str)
    parser.add_argument("size", help="File Size", type=str)
    parser.add_argument("active_time", help="File Active Time", type=str)
    parser.add_argument("full_path", help="File Full Path", type=str)

    # Optional arguments
    parser.add_argument("-d", "--debug", help="Debug Mode", type=bool, default=False)

    # Print version
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    # Parse arguments
    args = parser.parse_args()

    return args


def is_host_open(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        # s.connect((ip, int(port)))
        s.connect(("192.168.1.40", int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = parse_arguments()
    path = os.path.dirname(os.path.abspath(__file__))

    # This registration token comes from the client FCM SDKs.
    registration_token = registrationCodes.registration_token_samsung

    cred = credentials.Certificate(path + "/fir-tutorial-2-firebase-adminsdk.json")
    default_app = firebase_admin.initialize_app(cred)

    message = messaging.Message(
        notification=messaging.Notification(
            title='Descarga Completada',
            body='File: ' + args.name
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

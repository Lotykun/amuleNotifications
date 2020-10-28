# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import socket
import argparse
import sys
import pipes
import logging
import datetime
import firebase_admin
import yaml
from paramiko import SSHException
from paramiko import SSHClient
from paramiko.ssh_exception import NoValidConnectionsError
from scp import SCPClient
from pathlib import Path
from firebase_admin import credentials
from firebase_admin import messaging


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


def upload_file_to_host(ip, port, username, password, file_name, source_path, final_path):
    respuesta = {}
    ssh = SSHClient()
    ssh.load_system_host_keys()
    try:
        ssh.connect(hostname=ip,
                    port=port,
                    username=username,
                    password=password)

        sftp = ssh.open_sftp()
        sftp.chdir(final_path)
        try:
            remote_info = sftp.stat(final_path + file_name)
            respuesta['code'] = 0
            respuesta['remote_size'] = remote_info.st_size
        except IOError:
            print('copying file')
            logging.info('copying file')
            sftp.put(source_path, final_path + file_name)
            remote_info = sftp.stat(final_path + file_name)
            respuesta['code'] = 1
            respuesta['remote_size'] = remote_info.st_size
        ssh.close()
    except SSHException as e:
        print(str(e))
        logging.info(str(e))
        respuesta['code'] = -1
    except NoValidConnectionsError as e:
        print(str(e))
        logging.info(str(e))
        respuesta['code'] = -1
    return respuesta


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = parse_arguments()
    path = os.path.dirname(os.path.abspath(__file__)) + '/'
    x = datetime.datetime.now()
    file_log_name = x.strftime("%Y-%m-%d_%H-%M-%S") + "_" + "amulenotifications" + ".log"
    logFile = path + "logs/" + file_log_name
    logging.basicConfig(level=logging.INFO, filename=logFile)

    logging.info('INIT PROCESS:')
    logging.info('ARGS NAME: ' + args.name + 'ARGS FILE_PATH: ' + args.full_path)

    with open(path + 'parameters.yml') as file:
        parameters = yaml.load(file, Loader=yaml.FullLoader)

    file_path = args.full_path
    file_path_transformed = file_path.replace("\\", "")
    logging.info('FILE_PATH_TRANSFORMED: ' + file_path_transformed)

    # This registration token comes from the client FCM SDKs.
    registration_token = parameters['registration_tokens']['samsung']

    cred = credentials.Certificate(path + "fir-tutorial-2-firebase-adminsdk.json")
    default_app = firebase_admin.initialize_app(cred)

    message = messaging.Message(
        notification=messaging.Notification(
            title='Descarga Completada',
            body='File: ' + file_path
        ),
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                channel_id='default_channel'
            )
        ),
        token=registration_token,
    )
    response = messaging.send(message)
    print('Successfully sent Download message:', response)
    logging.info('Successfully sent Download message:' + response)

    response = upload_file_to_host(
        parameters['nas_data']['host'],
        parameters['nas_data']['port'],
        parameters['nas_data']['username'],
        parameters['nas_data']['password'],
        args.name,
        file_path_transformed,
        parameters['nas_data']['destination_path'])

    source_info = os.stat(file_path_transformed)
    source_size = source_info.st_size
    if response['code'] != -1 and response['remote_size'] == source_size:
        print('file exists in destination removing from source')
        os.remove(file_path_transformed)
        message = messaging.Message(
            notification=messaging.Notification(
                title='Descarga Copiada a NAS',
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
        print('Successfully sent Complete message:', response)
        logging.info('Successfully sent Complete message:' + response)
    logging.info('END PROCESS:')

    # Response is a message ID string.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

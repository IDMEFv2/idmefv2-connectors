'''
Useful helper functions for IDMEFv2
'''
import datetime
import uuid
import socket

def idmefv2_uuid() -> str:
    '''
    Generates a UUID 4

    Returns:
        str: a new UUID version 4
    '''
    return uuid.uuid4().urn[9:]

def idmefv2_convert_timestamp(ts: str) -> str:
    '''
    Convert Suricata timestamp

    Args:
        ts (str): timestamp in Suricata format

    Returns:
        str: timestamp in IDMEFv2 format
    '''
    i = datetime.datetime.fromisoformat(ts)
    return i.isoformat()

def idmefv2_my_local_ip() -> str:
    '''
    Returns local IP

    Returns:
        str: the local IP
    '''
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

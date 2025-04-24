'''
UUID generation for IDMEFv2
'''
import datetime
import uuid

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

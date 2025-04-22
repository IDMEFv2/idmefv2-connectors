'''
UUID generation for IDMEFv2
'''
import uuid

def idmefv2_uuid() -> str:
    '''
    Generates a UUID 4

    Returns:
        str: a new UUID version 4
    '''
    return uuid.uuid4().urn[9:]

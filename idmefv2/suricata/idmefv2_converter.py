import uuid
from .converter import Converter

def idmefv2_uuid():
    return uuid.uuid4().urn[9:]

class IDMEFv2Converter(Converter):
    IDMEFV2_TEMPLATE = {
        'Version': '2.0.3',
        'ID': idmefv2_uuid,
        'CreateTime': '$.timestamp',
    }

    def __init__(self):
        super().__init__(IDMEFv2Converter.IDMEFV2_TEMPLATE)

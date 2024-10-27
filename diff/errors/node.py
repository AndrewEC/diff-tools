class InvalidNodePropertiesException(Exception):

    _MESSAGE_TEMPLATE = 'Could not read Node from save file. Found an unrecognized property of "{}".'

    def __init__(self, unrecognized_property: str):
        super().__init__(InvalidNodePropertiesException._MESSAGE_TEMPLATE.format(unrecognized_property))

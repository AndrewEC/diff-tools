from pathlib import Path


class InvalidScanFileException(Exception):

    _MESSAGE_TEMPLATE = 'Scan file [{}] could not be read. Cause: [{}]'

    def __init__(self, scan_path: Path, cause: Exception):
        super().__init__(InvalidScanFileException._MESSAGE_TEMPLATE.format(scan_path, cause))

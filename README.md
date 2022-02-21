# diff-tools
Command line tools for detecting changes in the directory structure of a given folder.

**Important**: It is recommended to run the `CreateVenv.ps1` script before executing any of the below commands.

### scan
Utility to scan the structure of all folders and files in a given folder and write them to a YAML file.

Usage:
> python -m diff scan "C:\\" "C_scan_result.yml"

### latest
Utility to check for the following:
* If any file or folder has been removed/renamed since the last scan
* If any file size has changed since the last scan
* Optionally calculate and compare checksums to ensure file equality with previous scan results

Usage:
> python -m diff changes "C_scan_result.yml"

### changed
Utility to check the diff between two given folders. This will check the following:
* If any file or folder can be found in one folder but can't be found in the other
* If any file between the two folders has the same path but a different file size
* Optionally calculate and compare the checksum of two files to ensure equality

Usage:
> python -m diff between "C:\\" "D:\\"


### fingerprint
Utility to generate a checksum, or hash, or a specified file.
* If the file is below 200 MB in size the hash will be a true Shake 256 hash
* If the file is above 200 MB in size the hash will be a pseudo Shake 256 hash

Usage:
> python -m fingerprint "C:\\<path_to_file_to_fingerprint>"
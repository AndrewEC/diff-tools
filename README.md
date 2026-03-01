# diff-tools
Command line tools for detecting changes in the directory structure of a given folder.

## Cloning
To clone the project and the required submodules run:

    git clone --recurse-submodules https://github.com/AndrewEC/diff-tools.git

Once the project has been cloned run the `RunScript.ps1 Install` script. This will create a proper
virtual environment and install the dependencies specified in `requirements.txt`.

## Commands

### Scan

#### folder
Scans a directory, and all its nested contents, and write that structure to a YAML file.

The first argument specifies the directory to scan, the second argument specifies the path to the YAML file
where the scan results should be saved.

Usage:
> python -m diff scan folder "<path_to_folder_to_scan>" "scan_result.yml"

#### verify
Scans a directory, and all its nested contents, and compare the results of that scan to a previous
scan YML file and display the list of differences between each. The YML files can be generated
using the `scan folder` command.

The first argument specifies the directory to scan, the second argument specifies the path the existing YAML file
where the scan results from the last scan were stored.

Usage:
> python -m diff scan verify "<path_to_folder_to_scan>" "<path_to_existing_yml_file>"

### between
Scans two directories, and all the nested contents of each, and compare said structures to identify:
1. Files that are "similar" (similar refers to files that have the same name but a different file size or checksum).
2. Files exist in the first folder but not in the second.
3. Files exist in the second folder but not in the first.

Usage:
> python -m diff between "<path_to_first_folder_to_scan>" "<path_to_second_folder_to_scan>"

### checksum

#### calculate
Calculate a checksum, sometimes called a fingerprint, of a single file.

Usage:
> python -m diff checksum calculate "<path_to_file_to_compute_checksum_of>"

#### compare
Calculates the hashes of two different files and compares them for equality.

Usage:
> python -m diff checksum compare "<first_file>" "<second_file>"

#### verify
Verifies the checksum of a file. This will compute the checksum of the file the compare the
computed checksum to a previously computed checksum.

Usage:
> python -m diff checksum verify "<path_to_file_to_compute_checksum_of>" <previous_checksum>

## Flake8 and Dependency Auditing
Executing the `RunScript.ps1` will perform all the required tasks such as activating the proper
virtual environment, installing depdnencies, running Flake8 and pip-audit.

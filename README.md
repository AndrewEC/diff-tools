# diff-tools
Command line tools for detecting changes in the directory structure of a given folder.

## Cloning
To clone the project and the required submodules run:

    git clone --recurse-submodules https://github.com/AndrewEC/diff-tools.git

Once the project has been cloned run the `CreateVenv.ps1` script before executing any of the below commands.

## Commands

### scan folder
A command that will scan a directory, and all its nested contents, and write that structure to a YAML file.

The first argument specifies the directory to scan, the second argument specifies the path to the YAML file
where the scan results should be saved.

Usage:
> python -m diff scan folder "<path_to_folder_to_scan>" "scan_result.yml"

### scan verify
A command that will scan a directory, and all its nested contents, and compare the results of that scan to a previous
scan YML file. Much like the `diff between` command this will list the differences between the previous scan results
and the files that are currently on disk.

The first argument specifies the directory to scan, the second argument specifies the path the existing YAML file
where the scan results from the last scan were stored.

Usage:
> python -m diff scan verify "<path_to_folder_to_scan>" "<path_to_existing_yml_file>"

### between
A command that will scan two directories, and all the nested contents of each, and compare said structures to identify:
1. Files that are "similar" (similar refers to files that have the same name but a different file size or checksum).
2. Files exist in the first folder but not in the second.
3. Files exist in the second folder but not in the first.

Usage:
> python -m diff between "<path_to_first_folder_to_scan>" "<path_to_second_folder_to_scan>"

### checksum calculate
A command to calculate a checksum, sometimes called a fingerprint, of a single file.

Usage:
> python -m diff checksum calculate "<path_to_file_to_compute_checksum_of>"

### checksum verify
A command to verify the checksum of a file. This will compute the checksum of the file the compare the
computed checksum to a previously computed checksum.

Usage:
> python -m diff checksum verify "<path_to_file_to_compute_checksum_of>" <previous_checksum>

## Flake8 and Dependency Auditing
The `build.py` script run on the py-build-utils submodule and will run the Flake8 and pip-audit
modules against this project. Simply run the `CreateVenv.ps1` script first then run the build.py script.

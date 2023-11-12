# diff-tools
Command line tools for detecting changes in the directory structure of a given folder.

**Important**: It is recommended to run the `CreateVenv.ps1` script before executing any of the below commands.

### scan folder
A command that will scan a directory, and all its nested contents, and write that structure to a YAML file.

The first argument specifies the directory to scan, the second argument specifies the path to the YAML file
where the scan results should be saved.

Usage:
> python -m diff scan folder "<path_to_folder_to_scan>" "scan_result.yml"

### scan verify
A command that will scan a directory, and all its nested contents, and compare the results of that scan to a previous
scan YML file.

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

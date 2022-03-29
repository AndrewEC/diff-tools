import click

from .between import between_group
from .changes import changes_command
from .scan import scan_command
from .fingerprint import fingerprint_command


@click.group()
def main():
    pass


main.add_command(between_group)
main.add_command(changes_command)
main.add_command(scan_command)
main.add_command(fingerprint_command)


if __name__ == '__main__':
    main()

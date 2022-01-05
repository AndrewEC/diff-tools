import click

from .between import between
from .changes import changes
from .scan import scan
from .fingerprint import fingerprint


@click.group()
def main():
    pass


main.add_command(between)
main.add_command(changes)
main.add_command(scan)
main.add_command(fingerprint)


if __name__ == '__main__':
    main()

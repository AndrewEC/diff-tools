import click

from .scan import scan
from .between import between
from .checksum import checksum


@click.group()
def main():
    pass


main.add_command(scan)
main.add_command(between)
main.add_command(checksum)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)

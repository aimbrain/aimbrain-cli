"""
aimbrain

Usage:
  aimbrain videoconv
  aimbrain -h | --help
  aimbrain --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  aimbrain videoconv

Help:
  For help using this tool, please open an issue on the repository:
  https://bitbucket.org/aimbrain/aimbrain-cli
"""


from inspect import getmembers, isclass

from docopt import docopt

from aimbrain import __version__ as VERSION
from aimbrain.commands.videoconv import VideoConv


def main():
    """Main CLI entrypoint."""

    options = docopt(__doc__, version=VERSION)

    for k, v in options.iteritems():
        command = None
        if k == 'videoconv':
            command = VideoConv(v)
            command.run()
            break


if __name__ == "__main__":
    main()

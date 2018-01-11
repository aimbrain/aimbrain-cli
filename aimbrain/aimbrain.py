"""
aimbrain

Usage:
  aimbrain videoconv (blur|brighten|sharpen|contrast) <factor> --in=<input_file> --out=<output_file> --avconv=<avconv> --ffprobe=<ffprobe>
  aimbrain -h | --help
  aimbrain --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  aimbrain videoconv blur --by 1.5 --in=/home/aimbrain/auth.mov --out=/home/aimbrain/auth_blur.mov

Help:
  For help using this tool, please open an issue on the repository:
  https://bitbucket.org/aimbrain/aimbrain-cli
"""


from inspect import getmembers
from inspect import isclass

from docopt import docopt

from . import __version__ as VERSION
from commands.videoconv import VideoConv


def main():
    """Main CLI entrypoint."""
    print('hello world')
    options = docopt(__doc__, version=VERSION)

    cmd = None
    if options.get('videoconv'):
        cmd = VideoConv(options)

    cmd.run()

"""
aimbrain

Usage:
  aimbrain videoconv (blur|brighten|sharpen|contrast) <factor> --in=<input_file> --out=<output_file> --avconv=<avconv> --ffprobe=<ffprobe>
  aimbrain auth (face|voice) <biometrics>... --user-id=<uid> --api-key=<api_key> --secret=<secret> [--token=<token>] [--dev]
  aimbrain compare (face) <biometric1> <biometric2> --user-id=<uid> --api-key=<api_key> --secret=<secret> [--dev]
  aimbrain enroll (face|voice) <biometrics>... --user-id=<uid> --api-key=<api_key> --secret=<secret> [--dev]
  aimbrain -h | --help
  aimbrain --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  aimbrain videoconv blur 1.5 --in=/home/aimbrain/auth.mov --out=/home/aimbrain/auth_blur.mov --avconv=/path/to/avconv --ffprobe=/path/to/ffprobe

Help:
  For help using this tool, please open an issue on the repository:
  https://bitbucket.org/aimbrain/aimbrain-cli
"""


from inspect import getmembers
from inspect import isclass

from docopt import docopt

from . import __version__ as VERSION
from commands.api import Auth
from commands.api import Compare
from commands.api import Enroll
from commands.videoconv import VideoConv


def main():
    """Main CLI entrypoint."""
    options = docopt(__doc__, version=VERSION)

    cmd = None
    if options.get('videoconv'):
        cmd = VideoConv(options)
    elif options.get('auth'):
        cmd = Auth(options)
    elif options.get('compare'):
        cmd = Compare(options)
    elif options.get('enroll'):
        cmd = Enroll(options)

    cmd.run()

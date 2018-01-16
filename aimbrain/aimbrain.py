"""
aimbrain-cli

Usage:
  aimbrain-cli auth (face|voice) <biometrics>... --user-id=<uid> --api-key=<api_key> --secret=<secret> [--token=<token>] [--dev]
  aimbrain-cli compare (face) <biometric1> <biometric2> --user-id=<uid> --api-key=<api_key> --secret=<secret> [--dev]
  aimbrain-cli enroll (face|voice) <biometrics>... --user-id=<uid> --api-key=<api_key> --secret=<secret> [--dev]
  aimbrain-cli token (voice) --user-id=<uid> --api-key=<api_key> --secret=<secret> [--token=<token>] [--dev]
  aimbrain-cli videoconv (blur|brighten|sharpen|contrast) <factor> --in=<input_file> --out=<output_file> --avconv=<avconv> --ffprobe=<ffprobe>
  aimbrain-cli -h | --help
  aimbrain-cli --version

Options:
  Requests:
    --user-id=<uid>                         User ID in Aimbrain
    --api-key=<key>                         Your Aimbrain API key
    --secret=<secret>                       Your Aimbrain Secret
    --token=<token>                         Generate specific token for voice auth e.g. enroll-6 for 1-2-3
    --dev                                   Toggle to send requests to dev environment

  VideoConv:
    --in=<input_file>/--out=<output_file>   Input/Output file for videoconv
    --avconv=<avconv>/--ffprobe=<ffprobe>   Path to avconv/ffprobe

  Generic:
    -h --help                               Show this screen.
    --version                               Show version.

Examples:
  aimbrain-cli auth face /path/to/face_image.png --user-id=user --api-key=key --secret=secret --dev
  aimbrain-cli videoconv blur 1.5 --in=/home/aimbrain/auth.mov --out=/home/aimbrain/auth_blur.mov --avconv=/path/to/avconv --ffprobe=/path/to/ffprobe

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
from commands.api import Token
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
    elif options.get('token'):
        cmd = Token(options)

    cmd.run()

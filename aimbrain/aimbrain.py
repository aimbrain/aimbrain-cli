"""
aimbrain-cli

Usage:
  aimbrain-cli auth (face|voice) <biometrics> --user-id=<uid> --api-key=<api_key> --secret=<secret> [--token=<token>] [--dev|--local] [--device=<device>] [--system=<system>]
  aimbrain-cli compare (face) <biometric1> <biometric2> --user-id=<uid> --api-key=<api_key> --secret=<secret> [--dev|--local] [--device=<device>] [--system=<system>]
  aimbrain-cli enroll (face|voice) <biometrics>... --user-id=<uid> --api-key=<api_key> --secret=<secret> [--dev|--local] [--device=<device>] [--system=<system>]
  aimbrain-cli token (face|voice) --user-id=<uid> --api-key=<api_key> --secret=<secret> [--token=<token>] [--dev|--local] [--device=<device>] [--system=<system>]
  aimbrain-cli session --user-id=<uid> --api-key=<api_key> --secret=<secret> [--dev|--local] [--device=<device>] [--system=<system>]
  aimbrain-cli videoconv (blur|brighten|sharpen|contrast) <factor> --in=<input_file> --out=<output_file> --avconv=<avconv> --ffprobe=<ffprobe>
  aimbrain-cli -h | --help
  aimbrain-cli --version

Options:
  Requests:
    --user-id=<uid>                         User ID in Aimbrain
    --api-key=<key>                         Your Aimbrain API key
    --secret=<secret>                       Your Aimbrain Secret
    --token=<token>                         Generate specific token for voice auth e.g. enroll-6 for 1-2-3
    --device=<device>                       Device you are using [default: Generic Phone]
    --system=<system>                       OS of device [default: Generic OS]
    --dev                                   Toggle to send requests to dev environment: https://dev.aimbrain.com
    --local                                 Toggle to send requests to local environment: http://localhost:8080

  VideoConv:
    --in=<input_file>/--out=<output_file>   Input/Output file for videoconv
    --avconv=<avconv>/--ffprobe=<ffprobe>   Path to avconv/ffprobe

  Generic:
    -h --help                               Show this screen.
    --version                               Show version.

Examples:
  aimbrain-cli auth face /path/to/face_image.png --user-id=user --token=enroll-6 --api-key=key --secret=secret --dev
  aimbrain-cli videoconv blur 1.5 --in=/home/aimbrain/auth.mov --out=/home/aimbrain/auth_blur.mov --avconv=/path/to/avconv --ffprobe=/path/to/ffprobe

Help:
  For help using this tool, please open an issue on the repository:
  https://bitbucket.org/aimbrain/aimbrain-cli
"""


from docopt import docopt

from . import __version__ as VERSION
from commands.api import Auth
from commands.api import Compare
from commands.api import Enroll
from commands.api import Session
from commands.api import Token
from commands.videoconv import VideoConv


def main():
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
    elif options.get('session'):
        cmd = Session(options)

    cmd.run()

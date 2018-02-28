import json
import os
import subprocess

from PIL import Image


class VideoCaptureService(object):
    """
    Read video using avconv or ffmpeg in a subprocess.

    The API is modelled after cv2.VideoCapture, and in many cases is a drop-in
    replacement.
    """
    def __exit__(self, type, value, traceback):
        self.proc.kill()
        self.proc = None
        self.buf = None
        self.resize = False

    def __enter__(self):
        return self

    def __init__(self, filename, avconv, ffprobe):
        self.filename = filename
        self.convert_command = avconv
        self.probe_command = ffprobe

        self.proc = None

        self.info = self.get_info()
        streams = self.info.get('streams')
        if not streams:
            raise ValueError('No streams found')

        if streams[0].get('codec_type') != 'video':
            raise ValueError('No video stream found')

        self.width, self.height, self.resize = self.get_dimensions(streams[0])
        self.depth = 3  # TODO other depths
        self.open()

    def get_dimensions(self, stream):
        resize = False
        width = stream.get('width')
        height = stream.get('height')
        if width > 480 and height > 480 and width > height:
            resize = True
            height = int(480 * ((height * 1.0) / width))
            width = 480

        elif width > 480 and height > 480 and height > width:
            resize = True
            width = int(480 * ((width * 1.0) / height))
            height = 480

        return width, height, resize

    def open(self):
        # TODO decide what is best behavior, reopen or leave as it if
        # previously opened
        if self.is_opened():
            self.release()

        cmd = [
            self.convert_command,
            '-y',
            '-loglevel',
            'error',
            '-i',
            self.filename
        ]
        if self.resize:
            cmd += ['-vf', 'scale=%d:%d' % (self.width, self.height)]

        cmd += ['-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']

        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        self.buf = b''

    def is_opened(self):
        return self.proc is not None

    def read_blocks(self, nbytes):
        while len(self.buf) < nbytes:
            # Could poll here, but return code never seems to be set before we
            # fail at reading anyway
            if self.proc.returncode is not None:
                if self.proc.returncode < 0:
                    # TODO subprocess.CalledProcessError?
                    raise ValueError(
                        'Command exited with return code %d' % (
                            self.proc.returncode
                        )
                    )

                return False

            buf = self.proc.stdout.read(nbytes - len(self.buf))

            # Reading no data seems to be a reliable end-of-file indicator;
            # return code is not.
            if len(buf) == 0:
                break

            self.buf += buf

        return True

    def read(self):
        nbytes = self.width * self.height * self.depth
        retval = self.read_blocks(nbytes)
        if not retval:
            return False, None

        if len(self.buf) < nbytes:
            # We didn't get any data, assume end-of-file
            if len(self.buf) == 0:
                return False, None

            # We got some data but not enough, this is an error
            raise ValueError(
                'Not enough data at end of file, expected %d bytes, '
                'read %d' % (nbytes, len(self.buf))
            )

        image = Image.frombytes('RGB', (self.width, self.height), self.buf[:nbytes])
        self.buf = b''

        # If there is data left over, move it to beginning of buffer for next
        # frame
        if len(self.buf) > nbytes:
            # TODO this is a relatively slow operation, optimize
            self.buf = self.buf[nbytes:]

        return retval, image

    def get_info(self):
        # NOTE requires a fairly recent avprobe/ffprobe, older versions don't
        #      have -of json and only produce INI-like output
        # TODO parse old INI-like output
        cmd = '-loglevel error -of json -show_format -show_streams'.split()
        cmd.insert(0, self.probe_command)
        cmd.append(self.filename)
        output = subprocess.check_output(cmd, universal_newlines=True)

        return json.loads(output)


class AudioExtractor(object):

    def __exit__(self, type, value, traceback):
        terminated = self.proc.poll()
        if terminated is None:
            self.proc.kill()

        self.proc = None
        self.buf = None
        self.resize = False

    def __enter__(self):
        return self

    def __init__(self, in_filename, out_filename, avconv):
        self.in_filename = in_filename
        self.out_filename = out_filename
        self.convert_command = avconv
        self.proc = None

    def read_wav(self):
        return wav.read(self.out_filename)

    def read_binary(self):
        data = ''
        with open(self.out_filename, 'rb') as f:
            data = f.read()

        return data

    def extract(self, rate=16000):
        cmd = '{} -y -i {} -f wav -ar {} -ac 1 -vn {} -loglevel error'.format(
            self.convert_command,
            self.in_filename,
            int(rate),
            self.out_filename
        )

        self.proc = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
        code = self.proc.wait()
        if code != 0:
            raise DecodeError(
                'Failed to extract audio from video, return code %d' % code
            )

        if not os.path.exists(self.out_filename):
            raise DecodeError('Failed to extract audio from video')

import subprocess

import cv2
import numpy
from PIL import ImageEnhance
from PIL import ImageFilter

from aimbrain.commands.base import BaseCommand
from aimbrain.commands.utils.video_reader import AudioExtractor
from aimbrain.commands.utils.video_reader import VideoCaptureService


class VideoConv(BaseCommand):

    def __init__(self, options, *args, **kwargs):
        super(VideoConv, self).__init__(self, options, *args, **kwargs)

        self.input = options.get('--in')
        self.output = options.get('--out')
        self.avconv = options.get('--avconv')
        self.ffprobe = options.get('--ffprobe')

        self.brighten = options.get('brighten')
        self.blur = options.get('blur')
        self.sharpen = options.get('sharpen')
        self.contrast = options.get('contrast')

        self.factor = float(options.get('<factor>'))

    def get_video_data(self):
        """
        Get frames, width and height of video
        """

        frames = []
        width = None
        height = None
        with VideoCaptureService(self.input, self.avconv, self.ffprobe) as vcs:
            width = vcs.width
            height = vcs.height

            while True:
                ok, image = vcs.read()
                if not ok:
                    break

                frames.append(image)

        return frames, width, height

    def get_audio_file(self, audio_file='/tmp/audio.wav'):
        """
        Get audio from input, store it and return location

        Optional Arguments:
        audio_file <string> --- Path to output audio to
        """

        with AudioExtractor(self.input, audio_file, self.avconv) as ae:
            ae.extract()

        return audio_file

    def sharpen_video(self, frames):
        """
        Sharpen the video frames

        Arguments:
        frames <list> --- List of images
        """
        sharpened_frames = []
        for frame in frames:
            enhancer = ImageEnhance.Sharpness(frame)
            sharpened_frames.append(enhancer.enhance(self.factor))

        return sharpened_frames

    def brighten_video(self, frames):
        """
        Brighten the video frames

        Arguments:
        frames <list> --- List of images
        """

        brightened_frames = []
        for frame in frames:
            enhancer = ImageEnhance.Brightness(frame)
            brightened_frames.append(enhancer.enhance(self.factor))

        return brightened_frames

    def contrast_video(self, frames):
        """
        Change the video frames contrast

        Arguments:
        frames <list> --- List of images
        """

        contrasted_frames = []
        for frame in frames:
            enhancer = ImageEnhance.Contrast(frame)
            contrasted_frames.append(enhancer.enhance(self.factor))

        return contrasted_frames

    def blur_video(self, frames):
        """
        Blur the video frames

        Arguments:
        frames <list> --- List of images
        """

        blurred_frames = []
        for frame in frames:
            blurred_frames.append(
                frame.filter(ImageFilter.GaussianBlur(self.factor))
            )

        return blurred_frames

    def build_video(self, frames, width, height, video_file='/tmp/video.avi'):
        """
        Create a video from the given frames at a certain width and height

        Arguments:
        frames <list> --- List of images
        width <float> --- Width of desired video
        height <float> --- Height of desired video

        Optional Arguments:
        video_file <string> --- Path to output video file to
        """

        # Create the OpenCV VideoWriter
        video = cv2.VideoWriter(
            video_file,
            cv2.VideoWriter_fourcc(*"XVID"),
            30.0,
            (width, height),
        )

        for frame in frames:
            frame = frame.rotate(90)
            video.write(cv2.cvtColor(numpy.array(frame), cv2.COLOR_RGB2BGR))

        video.release()
        return video_file

    def combine_video_and_audio(self, video_file, audio_file):
        """
        Combine the video and audio files to create the final product

        Arguments:
        video_file <string> --- Path to a video file
        audio_file <string> --- Path to a audio file
        """

        cmd = [
            self.avconv,
            '-y',
            '-i',
            video_file,
            '-i',
            audio_file,
            '-c',
            'copy',
            self.output,
            '-loglevel',
            'error'
        ]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        proc.wait()

    def run(self):
        frames, width, height = self.get_video_data()
        audio_file = self.get_audio_file()

        print('Running videoconv operation')
        if self.brighten:
            frames = self.brighten_video(frames)

        elif self.blur:
            frames = self.blur_video(frames)

        elif self.sharpen:
            frames = self.sharpen_video(frames)

        elif self.contrast:
            frames = self.contrast_video(frames)

        video_file = self.build_video(frames, width, height)
        self.combine_video_and_audio(video_file, audio_file)
        print('Completed videoconv operation')

import cv2
import numpy
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter

from aimbrain.commands.base import BaseCommand
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
        frames =  []
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

    def sharpen_video(self, frames):
        sharpened_frames = []
        for frame in frames:
            enhancer = ImageEnhance.Sharpness(frame)
            sharpened_frames.append(enhancer.enhance(self.factor))

        return sharpened_frames

    def brighten_video(self, frames):
        brightened_frames = []
        for frame in frames:
            enhancer = ImageEnhance.Brightness(frame)
            brightened_frames.append(enhancer.enhance(self.factor))

        return brightened_frames

    def contrast_video(self, frames):
        contrasted_frames = []
        for frame in frames:
            enhancer = ImageEnhance.Contrast(frame)
            contrasted_frames.append(enhancer.enhance(self.factor))

        return contrasted_frames

    def blur_video(self, frames):
        blurred_frames = []
        for frame in frames:
            blurred_frames.append(
                frame.filter(ImageFilter.GaussianBlur(self.factor))
            )

        return blurred_frames

    def build_video(self, frames, width, height):
        # Create the OpenCV VideoWriter
        video = cv2.VideoWriter(
            self.output,
            cv2.VideoWriter_fourcc(*"XVID"),
            30.0,
            (width, height),
        )

        for frame in frames:
            frame = frame.rotate(90)
            video.write(cv2.cvtColor(numpy.array(frame), cv2.COLOR_RGB2BGR))

        video.release()

    def run(self):
        frames, width, height = self.get_video_data()

        if self.brighten:
            frames = self.brighten_video(frames)

        elif self.blur:
            frames = self.blur_video(frames)

        elif self.sharpen:
            frames = self.sharpen_video(frames)

        elif self.contrast:
            frames = self.contrast_video(frames)

        self.build_video(frames, width, height)

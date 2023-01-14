import io
import os

from flask import Flask, Response
from threading import Condition
from typing import Dict, Tuple

import libcamera
from libcamera import controls
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput

# Configuration Starts #
RESOLUTION = (1920, 1080)
FPS = 24
QF = 1 # Quality factor

AUTO_FOCUS = True
HDR = True
ROTATE_H = 1
ROTATE_V = 1

STREAM_PORT = 8764
# Configuration Ends #

class Camera:

    def __init__(
            self,
            resolution: Tuple[int],
            fps: int,
            qf: float,
            rotate_h: bool,
            rotate_v: bool,
            autofocus: bool,
            hdr: bool
    ):
        self.resolution = resolution
        self.fps = fps
        self.qf = qf

        self.controls = self._setup_controls(autofocus)
        self.api = self._get_api_object(rotate_h, rotate_v)

        if hdr:
            os.system('v4l2-ctl --set-ctrl wide_dynamic_range=1 -d /dev/v4l-subdev0')

    def _setup_controls(self, autofocus: bool) -> Dict:
        base_speed = 1000000 # 1 second
        data = {
            "FrameDurationLimits": (int(base_speed/(2*self.fps)), base_speed) # Shutter speed ranges from 1/2*FPS to 1 sec
        }
        if autofocus:
            data["AfMode"] = controls.AfModeEnum.Continuous
        return data

    def _get_api_object(self, rotate_h: bool, rotate_v: bool):
        api_obj = Picamera2()
        api_obj.configure(api_obj.create_video_configuration(
            main={"size": self.resolution},
            controls=self.controls,
            transform=libcamera.Transform(
                hflip=1 if rotate_h else 0,
                vflip=1 if rotate_v else 0,
            )
        ))
        return api_obj

    def up(self, output: StreamingOutput):
        res_qf = (RESOLUTION[0] * RESOLUTION[1]) / (1920 * 1080)
        self.api.start_recording(MJPEGEncoder(int(self.fps*self.qf*res_qf*1024*1024)), FileOutput(output))

    def down(self):
        self.api.stop_recording()

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


app = Flask(__name__)

def get_img():
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame

        yield (
            b'--frame\r\n'
            b'Content-Type:image/jpeg\r\n'
            b'Content-Length: ' + f'{len(frame)}'.encode() + b'\r\n'
            b'\r\n' + frame + b'\r\n'
       )

@app.route("/")
def index():
    return Response(get_img(), mimetype='multipart/x-mixed-replace; boundary=frame')

output = StreamingOutput()
camera = Camera(RESOLUTION, FPS, QF, ROTATE_H, ROTATE_V, AUTO_FOCUS, HDR)
camera.up(output)

try:
    app.run(host='0.0.0.0', port=STREAM_PORT, threaded=True)
finally:
    camera.down()

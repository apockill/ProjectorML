from argparse import ArgumentParser

import cv2
import numpy as np

from easyinference.models import DeeplabImageSegmenter, ObjectDetector

from hanover_resources.communication import Device
from hardware.camera import Camera
from hardware.projector import Projector
from utils import draw_utils


class Demo:
    CHECK_FOR_HUMANS = 5  # Check for humans every X frames
    HUMAN_PIXEL_THRESH = 5000  # Number of human pixels to count as an 'alarm'

    def __init__(self, camera, projector, segmentation_brain, detector_brain,
                 device):

        self.cam = camera
        self.prj = projector
        self.segmenter = segmentation_brain
        self.detector = detector_brain
        self.device = device

    def run(self):
        self.cam.show()
        count = 0

        while cv2.waitKey(10) != ord('q'):
            # Get a frame
            frame = self.cam.read()
            count += 1

            canvas = self.prj.empty_frame
            canvas = self.draw_segmentations(frame)

            # Send a signal if there are humans in the frame
            if count % self.CHECK_FOR_HUMANS == 0:
                warped = self.prj.get_warped_frame(canvas)
                human_pixels = (warped == [255, 255, 255]).sum()
                print("Human pixels", human_pixels)
                is_person = human_pixels > self.HUMAN_PIXEL_THRESH
                self.device.set_person_status(is_person)

            self.draw_predictions(frame, canvas)
            cv2.imshow("Labels", canvas)
            self.prj.render_to_camera(canvas, wait=False)

        self.cam.close()

    def draw_segmentations(self, detection_frame):
        if self.segmenter is None: return
        segmentation = self.segmenter.predict(detection_frame)
        return segmentation.colored

    def draw_predictions(self, detection_frame, canvas_frame):
        if self.detector is None: return

        det_preds = self.detector.predict([detection_frame])[0]

        # Draw the labels onto the empty frame
        for pred in det_preds:
            draw_utils.draw_label(canvas_frame, pred.rect, pred.name)
        return canvas_frame


def main(args):
    cam = Camera(0)
    projector = Projector(3)
    projector.load_configuration(args.calibration_path)

    segmenter_brain = DeeplabImageSegmenter.from_path(args.segment_path,
                                                      args.segment_map)

    detector_brain = ObjectDetector.from_path(args.detector_path,
                                              args.detector_labels)

    device = Device(args.device_port)

    demo = Demo(camera=cam,
                projector=projector,
                segmentation_brain=segmenter_brain,
                detector_brain=None,
                device=device)
    demo.run()


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Run a video/webcam through the Image Classification model"
                    " and watch it live. Press q to Exit.")
    parser.add_argument("-s", "--segment-path", type=str, required=True,
                        help="The path to the Image Segmentation model you would like to run")
    parser.add_argument("-m", "--segment-map", type=str, required=True,
                        help="The path to the label_map.json for the image segmentation model")

    parser.add_argument("-o", "--detector-path", type=str, required=True,
                        help="The path to the Object Detection model you would like to run")
    parser.add_argument("-l", "--detector-labels", type=str, required=True,
                        help="The path to the labels.json for the Detection model")

    parser.add_argument("-c", "--calibration-path", type=str, required=True,
                        help="The path to the calibration.json file for the projector mapping to work." \
                             "If this argument is absent, the projector will re-calibrate.")

    parser.add_argument("-d", "--device_port", type=str, required=True,
                        help="The path to the calibration.json file for the projector mapping to work." \
                             "If this argument is absent, the projector will re-calibrate.")
    args = parser.parse_args()
    main(args)

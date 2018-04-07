from argparse import ArgumentParser

import cv2
import numpy as np

from hardware.camera import Camera
from hardware.projector import Projector
from easyinference.models import \
    DeeplabImageSegmenter, FCRNDepthPredictor, ObjectDetector
from utils import draw_utils


class Demo:
    def __init__(self, camera, projector, segmentation_brain, detector_brain):

        self.cam = camera
        self.prj = projector
        self.segmenter = segmentation_brain
        self.detector = detector_brain

    def run(self):
        self.cam.show()

        while cv2.waitKey(10) != ord('q'):

            # Get a frame
            frame = self.cam.read()
            h, w = frame[:2]

            canvas = self.prj.empty_frame

            self.draw_predictions(frame, canvas)
            cv2.imshow("Labels", canvas)
            self.prj.render_to_camera(canvas, wait=False)

        self.cam.close()

    def draw_predictions(self, detection_frame, canvas_frame):
        det_preds = self.detector.predict([detection_frame])[0]

        # Draw the labels onto the empty frame
        for pred in det_preds:
            draw_utils.draw_label(canvas_frame, pred.rect, pred.name)



def main(args):
    cam = Camera(0)
    projector = Projector(3)
    projector.load_configuration(args.calibration_path)

    segmenter_brain = DeeplabImageSegmenter.from_path(args.segment_path,
                                                      args.segment_map)
    # depth_brain = FCRNDepthPredictor.from_path(args.depth_path)
    detector_brain = ObjectDetector.from_path(args.detector_path,
                                              args.detector_labels)

    demo = Demo(camera=cam,
                projector=projector,
                segmentation_brain=segmenter_brain,
                detector_brain=detector_brain)
    demo.run()


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Run a video/webcam through the Image Classification model"
                    " and watch it live. Press q to Exit.")
    parser.add_argument("-d", "--depth-path", type=str, required=True,
                        help="The path to the Depth Prediction model you would like to run")

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
    args = parser.parse_args()
    main(args)

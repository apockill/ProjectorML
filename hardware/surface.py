import cv2
import numpy as np

from hardware.camera import Camera
from utils.draw_utils import draw_cross, draw_polygon


class Surface:
    def __init__(self, cam_points, prj_points):
        """
        :param cam_points: A list of points in the camera coordinate grid
        :param prj_points: A corresponding list of points in the projector grid
        """
        self.cam_points = np.array(cam_points)
        self.prj_points = np.array(prj_points)
        self._to_camera_mat = self._get_affine_warp(prj_points,
                                                    cam_points)
        self._to_projector_mat = self._get_affine_warp(cam_points,
                                                       prj_points)

    def warp_to_camera(self, projector_frame, new_dimensions):
        """Warps a projector frame such that if projected, it would appear on
        the cameras perspective as unwarped."""
        to_warp = self.mask_frame(projector_frame)

        warped = cv2.warpPerspective(to_warp,
                                     self._to_projector_mat,
                                     new_dimensions)

        return warped

    def mask_frame(self, projector_frame):
        empty = np.zeros_like(projector_frame)
        mask = cv2.fillPoly(empty, [self.cam_points], (255, 255, 255))
        masked = cv2.bitwise_and(projector_frame, mask)
        return masked

    @staticmethod
    def _get_affine_warp(from_pts, to_pts):
        """
        This will generate a function that will work like this function(x1,
        y1, z1) and returns (x2, y2, z2), where x1, y1, z1 are form the
        "fromPts" coordinate grid, and the x2, y2, z2 are from the "toPts"
        coordinate grid.

        It does this by using openCV's estimateAffine3D
        """
        src = np.float32(from_pts)
        dst = np.float32(to_pts)
        warp_mat = cv2.getPerspectiveTransform(src, dst)
        return warp_mat


# Instructions for SurfaceFactory
instructions_text_1 = """
Great! Now click on the open window. It should display a live view of the camera

Move your mouse around the window. Notice how the projector is moving around an X?
Your goal is to move that X onto four corners of a flat plane. Say, a table or wall. 

Move that X onto the corner of a table, then left click. Now move your mouse- see 
the line that's following it? Move it to the next corner. Then the next.

Once 4 corners have been selected, you will move to the next step.
"""

instructions_text_2 = """
Fantastic! You have made 4 points on the projectors point of view. Now it's time to 
tell the camera where each projectors point actually is in the camera coordinates!

What does that mean? Simply click on the projected X that should be on your screen 
using your mouse. 

This will happen four times, then you will be done creating the surface!
"""


class SurfaceFactory:
    CALIBRATION_COLOR = (255, 255, 255)

    def __init__(self, cam, prj):
        self.cam = cam
        self.prj = prj

    def create_surface(self):
        print(instructions_text_1)
        projector_points = self._get_projector_points()
        print(instructions_text_2)
        camera_points = self._get_camera_points(projector_points)
        return Surface(camera_points, projector_points)

    def _get_camera_points(self, prj_points):
        """Get the camera coordinates for each projector point"""
        # Create the function globals
        cam_points = []

        def mouse_callback(event, x, y, flags, params):
            if event == cv2.EVENT_LBUTTONDOWN:
                cam_points.append([x, y])

        # Set up window and callbacks
        win_name = "Click on all of the projected crosses on the camera view!"
        cv2.namedWindow(win_name)
        cv2.setMouseCallback(win_name, mouse_callback)

        while True:
            _, img = self.cam.read()
            frame = self.prj.empty_frame
            draw_cross(frame,
                       prj_points[len(cam_points)],
                       self.CALIBRATION_COLOR, 30)
            cv2.imshow(win_name, img)
            self.prj.render(frame)
            if len(cam_points) == 4:
                cv2.destroyWindow(win_name)
                return cam_points

    def _get_projector_points(self):
        """Get 4 surface points from the projector perspective, using a mouse"""
        # Function-wide Globals
        points = []  # [[x, y], [x, y], [x, y]]
        curr_proj_point = [None, None]

        # Get frame sizes
        _, img = self.cam.read()
        cam_h, cam_w, _ = img.shape
        prj_h, prj_w, _ = self.prj.empty_frame.shape

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_MOUSEMOVE:
                # Adjust the X and Y to stretch to the projectors FOV
                curr_proj_point[0] = int((prj_w / cam_w) * x)
                curr_proj_point[1] = int((prj_h / cam_h) * y)
                frame = self.prj.empty_frame
                draw_cross(frame,
                           tuple(curr_proj_point),
                           self.CALIBRATION_COLOR, 30)
                draw_polygon(frame, points + [curr_proj_point],
                             self.CALIBRATION_COLOR, 6)
                self.prj.render(frame)
            if event == cv2.EVENT_LBUTTONDOWN:
                if curr_proj_point[0] is None: return
                points.append(tuple(curr_proj_point))

        # Set up window and callbacks
        win_name = "Move mouse around to get points in the REAL WORLD view"
        cv2.namedWindow(win_name)
        cv2.setMouseCallback(win_name, mouse_callback)

        while True:
            _, img = self.cam.read()
            cv2.imshow(win_name, img)
            cv2.waitKey(1)
            if len(points) == 4:
                cv2.destroyWindow(win_name)
                return points

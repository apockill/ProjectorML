import json
from random import shuffle

import cv2
import numpy as np
import screeninfo

from hardware.surface import Surface




class Projector:
    # Shift the window so that the borders are not projected.
    # TODO (Alex): Find something that can render fullscreen-borderless
    WINDOW_Y_SHIFT = -35

    def __init__(self, screen_id, surfaces=None):
        """
        :param screen_id: An integer number representing which monitor you
        want to project to.
        :param surfaces: A list of Surface objects representing what areas
        are projectable. These can be gotten using the configure_projector.py
        script.
        """

        self.monitor = screeninfo.get_monitors()[screen_id]
        self.window_name = "Projector_Window"
        self.surfaces = [] if surfaces is None else surfaces

        # Render a single frame to create the projector window
        self.render(self.empty_frame)
        cv2.moveWindow(self.window_name, self.monitor.x,
                       self.monitor.y + self.WINDOW_Y_SHIFT)

    def render(self, frame, wait=True):
        cv2.imshow(self.window_name, frame)
        if wait:
            cv2.waitKey(1)

    def render_to_camera(self, frame, wait=True):
        """Draws a frame such that from the cameras perspective it's unwarped
        :param frame: A cv2 BGR frame
        :param wait: If true, it will render with cv2.waitKey(1) """
        # Create an empty frame to draw all the warped surfaces onto
        dims = (self.monitor.width, self.monitor.height)

        # Chose the correct input type if frame is grayscale
        if len(frame.shape) == 2:
            draw_frame = np.zeros(dims[::-1], dtype=np.uint8)
        else:
            draw_frame = self.empty_frame

        # Warp each surface, and paste them to the draw_frame
        for surface in self.surfaces:
            warped = surface.warp_to_camera(frame, dims)
            draw_frame = cv2.bitwise_or(draw_frame, warped)
        self.render(draw_frame, wait=wait)

    @property
    def empty_frame(self):
        """ Return an empty black frame of the same size of the window """
        return np.zeros((self.monitor.height, self.monitor.width, 3),
                        dtype=np.uint8)

    def load_configuration(self, filename):
        """ Loads surface configurations from a filename """
        config = json.load(open(filename, "r"))
        self.surfaces = [Surface(s["cam_points"], s["prj_points"])
                         for s in config]

    def save_configuration(self, filename):
        """ Saves surface configurations to a filename """
        config = [{"cam_points": s.cam_points.tolist(),
                   "prj_points": s.prj_points.tolist()}
                  for s in self.surfaces]
        json.dump(config, open(filename, "w"))

    def close(self):
        cv2.destroyWindow(self.window_name)

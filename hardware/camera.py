from time import time

import cv2
from threading import Thread


class Camera(Thread):
    """ A threaded camera class that constantly grabs frames and serves them
    from the camera.read() function """

    def __init__(self, cam_id, record_to=None):
        super().__init__()
        self.cap = cv2.VideoCapture(cam_id)
        self.running = True
        self.latest_frame = None
        self.show_screen = False
        self.window_name = "Camera View"

        # Recording Video
        self.writer = None
        self.record_to = record_to

        ret, frame = self.cap.read()
        if not ret: raise IOError("Unable to get frames from camera!")
        self.latest_frame = frame
        self.latest_tstamp = time()

        # Start the main camera loop
        self.start()

    def run(self):
        """Constantly grab frames from the camera and cache them"""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Camera stopped returning frames! Ending camera thread.")
                break
            self.latest_tstamp = time()
            self.latest_frame = frame

            if self.record_to is not None:
                if self.writer is None:
                    h, w = frame.shape[:2]
                    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                    self.writer = cv2.VideoWriter(self.record_to, fourcc, 24,
                                                  (w, h),
                                                  True)
                self.writer.write(frame)

            if self.show_screen:
                cv2.imshow(self.window_name, frame)

    def read(self):
        """Return the latest frame and timestamp from the camera"""
        latest = self.latest_frame
        return self.latest_tstamp, latest.copy()

    def show(self):
        """Show the current camera view to screen """
        cv2.namedWindow(self.window_name)
        self.show_screen = True

    def hide(self):
        """Hide the camera window"""
        self.show_screen = False
        cv2.destroyWindow(self.window_name)

    def close(self):
        """Stop the thread and close the camera capture"""
        self.running = False
        self.join()
        self.cap.release()
        if self.writer:
            self.writer.release()

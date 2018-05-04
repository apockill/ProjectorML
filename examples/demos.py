import cv2
import numpy as np

from utils.vision_utils import isolate_color

# Define globals
mouse_x, mouse_y, mouse_clicked = 0, 0, False


def wait_till_key(key):
    print("Press", key, "to continue!")
    while cv2.waitKey(1) != ord(key): pass


def draw_edged(cam, projector):
    cam.show()

    while cv2.waitKey(1) != ord('q'):
        _, frame = cam.read()

        # ret, thresh = cv2.threshold(frame, 200, 255, cv2.THRESH_TOZERO_INV)
        # # thresh = cv2.inRange(frame, (0, 0, 0), (100, 100, 100))
        # thresh = isolate_color(frame, [0, 0, 0], [0, 200, 200])
        # cv2.imshow("Theshed", thresh)

        # # Close the image
        # kernel = np.ones((5, 5), np.uint8)
        # closing = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        # cv2.imshow("Closed", closing)
        # edges = cv2.Canny(closing, 100, 200)

        edges = cv2.Canny(frame, 100, 200)

        projector.render_to_camera(edges)


def draw_edged_snapshot(cam, projector):
    cam.show()
    while cv2.waitKey(1) != ord('q'):
        _, frame = cam.read()
        white_frame = np.full(frame.shape, 255, dtype=np.uint8)
        projector.render_to_camera(white_frame)

        wait_till_key(' ')

        _, frame = cam.read()

        edges = cv2.Canny(frame, 100, 200)
        print(edges)
        cv2.imshow("Camera", frame)
        projector.render_to_camera(edges)

        wait_till_key(' ')


def draw_inverted(cam, projector):
    cam.show()
    while cv2.waitKey(1) != ord('q'):

        _, frame = cam.read()
        white_frame = np.full(frame.shape, 0, dtype=np.uint8)
        projector.render_to_camera(white_frame)

        wait_till_key(' ')

        _, frame = cam.read()
        inverted = 255 - frame
        projector.render_to_camera(inverted)

        wait_till_key(' ')


def draw_pointer(cam, projector, background_color=(255, 255, 255)):
    """ A demo coroutine that draws the mouse cursor on the camera stream """
    cam.show()

    def mouse_move(event, x, y, flags, param):
        global mouse_x, mouse_y, mouse_clicked
        if event == cv2.EVENT_MOUSEMOVE:
            mouse_x, mouse_y = x, y
        if event == cv2.EVENT_LBUTTONDOWN:
            mouse_clicked = True
        if event == cv2.EVENT_LBUTTONUP:
            mouse_clicked = False

    cv2.setMouseCallback(cam.window_name, mouse_move)

    while cv2.waitKey(1) != ord('q'):
        _, frame = cam.read()
        if frame is None: break

        proj = np.full_like(projector.empty_frame, background_color)
        if mouse_clicked:
            proj = cv2.circle(proj,
                              (mouse_x, mouse_y), 10,
                              (0, 255, 0), thickness=-1)
        projector.render_to_camera(proj)




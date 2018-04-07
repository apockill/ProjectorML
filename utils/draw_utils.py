import cv2
import numpy as np


def apply_grid_overlay(img, rows, cols, color=(255, 255, 255)):
    """Draw a grid on all black parts of an image, while ignoring colors"""
    grid = np.zeros_like(img)
    draw_grid(grid, rows, cols, color)
    labeled_pixels = img != [0, 0, 0]
    grid[labeled_pixels] = 0
    grid[labeled_pixels] = img[labeled_pixels]


def draw_grid(img, rows, cols, color=(255, 255, 255)):
    # size = int((img.shape[0] * img.shape[1]) ** .5 / (rows * cols) ** .5)
    width = int(img.shape[1] / cols)
    height = int(img.shape[0] / rows)

    for row in range(0, rows):
        for col in range(0, cols):
            cv2.line(img, (width * row, height * col),
                     (img.shape[1], height * (col)), color, 1, 1)
            cv2.line(img, (width * row, height * col),
                     (width * (row), img.shape[0]), color, 1, 1)


def draw_cross(img, center, color, size):
    img = cv2.line(img,
                   (int(center[0] - size / 2), int(center[1] - size / 2)),
                   (int(center[0] + size / 2), int(center[1] + size / 2)),
                   color, thickness=3)
    img = cv2.line(img,
                   (int(center[0] + size / 2), int(center[1] - size / 2)),
                   (int(center[0] - size / 2), int(center[1] + size / 2)),
                   color, thickness=3)


def draw_polygon(img, points, color, thickness):
    """Draw an n-point polygon, and it connects the last and first points"""
    if not len(points): return img

    for i in range(len(points) - 1):
        img = cv2.line(img,
                       tuple(points[i]),
                       tuple(points[i + 1]),
                       color,
                       thickness=thickness)
    img = cv2.line(img,
                   tuple(points[-1]),
                   tuple(points[0]),
                   color,
                   thickness=thickness)


def draw_label(img, rect, class_name, color=(255, 255, 255), thickness=1):
    # cv2.rectangle(img,
    #               (int(rect[0]), int(rect[1])),
    #               (int(rect[2]), int(rect[3])),
    #               color, thickness=thickness)
    cv2.putText(img,
                text=class_name,
                org=(int(rect[2]), int(rect[3])),
                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                fontScale=.5,
                color=color,
                thickness=thickness)

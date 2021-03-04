import numpy as np
import cv2
import logging
import os


from detection import detect_faces
from utils import create_dirs

lgr = logging.getLogger(__name__)

def anonymize_face_simple(image, factor=3.0):
    # automatically determine the size of the blurring kernel based
    # on the spatial dimensions of the input image
    (h, w) = image.shape[:2]
    kW = int(w / factor)
    kH = int(h / factor)
    # ensure the width of the kernel is odd
    if kW % 2 == 0:
        kW -= 1
    # ensure the height of the kernel is odd
    if kH % 2 == 0:
        kH -= 1
    # apply a Gaussian blur to the input image using our computed
    # kernel size
    return cv2.GaussianBlur(image, (kW, kH), 0)


def anonymize_face_pixelate(image, blocks=3):
    # divide the input image into NxN blocks
    (h, w) = image.shape[:2]
    xSteps = np.linspace(0, w, blocks + 1, dtype="int")
    ySteps = np.linspace(0, h, blocks + 1, dtype="int")
    # loop over the blocks in both the x and y direction
    for i in range(1, len(ySteps)):
        for j in range(1, len(xSteps)):
            # compute the starting and ending (x, y)-coordinates
            # for the current block
            startX = xSteps[j - 1]
            startY = ySteps[i - 1]
            endX = xSteps[j]
            endY = ySteps[i]
            # extract the ROI using NumPy array slicing, compute the
            # mean of the ROI, and then draw a rectangle with the
            # mean RGB values over the ROI in the original image
            roi = image[startY:endY, startX:endX]
            (B, G, R) = [int(x) for x in cv2.mean(roi)[:3]]
            cv2.rectangle(image, (startX, startY), (endX, endY),
                          (B, G, R), -1)
    # return the pixelated blurred image
    return image


def blur_file( path, simple=False, output = '/tmp/blur-out/'):
    """
    Detect Faces in a file then blur the bounding boxes,
    Writes the blurred image to a new file in output
    :param path:
    :param simple:
    :param output:
    :return:
    """
    lgr.debug(f'Blur Image at Path: {path}')

    cv2_image, faces = detect_faces(path)

    faces_count = len(faces)

    for (x, y, w, h) in faces:
        lgr.debug(f'Face: x{x} y{y} w{w} h{h}')
        # Draw a rectangle around the faces
        cv2.rectangle(cv2_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        face = cv2_image[y: (y + h), x: (x + w)]

        if simple:
            face = anonymize_face_simple(face, factor=3.0)
        else:
            face = anonymize_face_pixelate(face, )

        cv2_image[y:(y + h), x:(x + w)] = face

    create_dirs(output)

    filename = os.path.basename(path)
    filename = output + filename
    cv2.imwrite(filename, cv2_image)

    return faces_count

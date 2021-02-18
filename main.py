import cv2
import argparse
import os
import logging
import numpy as np

lgr = logging.getLogger(__name__)


cascPath = "haarcascade_frontalface_default.xml"
# Create the haar cascade
faceCascade = cv2.CascadeClassifier(cascPath)


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


def blur(path):
    lgr.info(f'Blurring Image: {path}')
    # Read the image
    image = cv2.imread(path)
    (h, w) = image.shape[:2]
    lgr.info(f'HW-{h} {w}')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    lgr.info("Found {0} faces!".format(len(faces)))
    lgr.info(faces)

    for (x, y, w, h) in faces:
        lgr.info(f'Face: x{x} y{y} w{w} h{h}')
        # Draw a rectangle around the faces
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        face = image[y: (y + h), x: (x + w)]

        # face = anonymize_face_simple(face, factor=3.0)
        face = anonymize_face_pixelate(face, )
        image[y:(y + h), x:(x + w)] = face


    output = '/tmp/blur-out/'
    filename = os.path.basename(path)

    filename = output + filename
    cv2.imwrite(filename, image)


def fs_path(string):
    # print(string)
    if os.path.exists(string):
        return string
    else:
        raise FileNotFoundError(string)


image_file_extensions = ['.jpeg','.jpg','.png','.bmp']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', type=fs_path, nargs='+', help='Paths to Images or Folders containing images')
    args = parser.parse_args()

    for path in args.paths:
        if os.path.isfile(path):
            blur(path)
        elif os.path.isdir(path):

            for file in os.listdir(path):
                filename = os.fsdecode(file)
                if any([ filename.endswith(extension) for extension in image_file_extensions ]):
                    image_path = os.path.join(path, filename)
                    blur(image_path)
                else:
                    # Skip non image
                    continue
        else:
            lgr.error(f'Unknown Path: {path}')


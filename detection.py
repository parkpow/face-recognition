import cv2
import logging

lgr = logging.getLogger(__name__)


cascPath = "haarcascade_frontalface_default.xml"
# Create the haar cascade
faceCascade = cv2.CascadeClassifier(cascPath)


def detect_faces(image_path):
    """
    Detects faces in an image at path
    :param image_path:
    :return: Faces bounding box
    :rtype: list
    """

    # Read the image
    image = cv2.imread(image_path)
    (h, w) = image.shape[:2]
    lgr.debug(f'HW-{h} {w}')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    lgr.debug("Found {0} faces".format(len(faces)))
    lgr.debug(faces)

    return image, faces


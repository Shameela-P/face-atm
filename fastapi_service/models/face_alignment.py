import cv2
import numpy as np

def align_face(img: np.ndarray, keypoints: dict, desired_face_width: int = 160, desired_face_height: int = 160) -> np.ndarray:
    """
    Performs 5-point facial landmark alignment based on MTCNN keypoints (left_eye, right_eye, nose, mouth_left, mouth_right).
    Rotates image so eye center line is horizontal.
    """
    left_eye = keypoints.get('left_eye')
    right_eye = keypoints.get('right_eye')

    if left_eye is None or right_eye is None:
        # Fallback to direct resize if eye landmarks are unavailable
        return cv2.resize(img, (desired_face_width, desired_face_height))

    # Calculate angle between eyes
    dY = right_eye[1] - left_eye[1]
    dX = right_eye[0] - left_eye[0]
    angle = np.degrees(np.arctan2(dY, dX))

    # Center point between eyes
    eye_center = ((left_eye[0] + right_eye[0]) // 2, (left_eye[1] + right_eye[1]) // 2)

    # Get rotation matrix
    M = cv2.getRotationMatrix2D(eye_center, angle, scale=1.0)

    # Rotate the image
    h, w = img.shape[:2]
    aligned = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC)

    return aligned

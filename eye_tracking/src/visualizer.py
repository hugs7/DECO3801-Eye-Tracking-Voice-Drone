from typing import Optional, Tuple

import cv2
import numpy as np
from scipy.spatial.transform import Rotation

from camera import Camera
from face import Face
from utils import transforms

AXIS_COLORS = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]


class Visualizer:
    def __init__(self, camera: Camera, center_point_index: int):
        self._camera = camera
        self._center_point_index = center_point_index
        self.image: Optional[np.ndarray] = None

    def set_image(self, image: np.ndarray) -> None:
        self.image = image

    def flip_image(self) -> None:
        flipped_image = transforms.flip_image(self.image)
        self.set_image(flipped_image)

    def draw_bbox(self, bbox: np.ndarray, color: Tuple[int, int, int] = (0, 255, 0), lw: int = 1) -> None:
        assert self.image is not None
        assert bbox.shape == (2, 2)
        bbox = np.round(bbox).astype(np.int32).tolist()
        cv2.rectangle(self.image, tuple(bbox[0]), tuple(bbox[1]), color, lw)

    @staticmethod
    def _convert_pt(point: np.ndarray) -> Tuple[int, int]:
        return tuple(np.round(point).astype(np.int32).tolist())

    def draw_points(self, points: np.ndarray, color: Tuple[int, int, int] = (0, 0, 255), size: int = 3) -> None:
        """
        Draws points from 2D image coordinates onto the image (direct drawing).
        """
        assert self.image is not None
        assert points.shape[1] == 2
        for pt in points:
            pt = self._convert_pt(pt)
            cv2.circle(self.image, pt, size, color, cv2.FILLED)
    
    def draw_bounds(self, points):
        print (points[0][0], points[0][1])
        color=(0, 0, 255)
        if (points[0][0] >= 1200):
            overlay = self.image.copy()
            # Draw the filled rectangle on the overlay
            cv2.rectangle(overlay, (2000,0), (1200, 1300), color, -1)

            # Set the transparency level
            alpha = 0.3  # Transparency factor (0.0 - 1.0)
    
            # Blend the overlay with the original image to get the semi-transparent effect
            cv2.addWeighted(overlay, alpha, self.image, 1 - alpha, 0, self.image)
            cv2.putText(self.image, 'Looking left', (1250, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA, False)
        elif (points[0][0] <= 300):
            overlay = self.image.copy()
            # Draw the filled rectangle on the overlay
            cv2.rectangle(overlay, (300, 0), (-100, 1300), color, -1)

            # Set the transparency level
            alpha = 0.3  # Transparency factor (0.0 - 1.0)
    
            # Blend the overlay with the original image to get the semi-transparent effect
            cv2.addWeighted(overlay, alpha, self.image, 1 - alpha, 0, self.image)
            cv2.putText(self.image, 'Looking right', (50, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA, False)


    
            
        


    def draw_3d_points(
        self, points3d: np.ndarray, color: Tuple[int, int, int] = (255, 0, 255), size=3, clamp_to_screen: bool = False
    ) -> None:
        """
        Draw points from 3D world coordinates onto the image.
        """
        assert self.image is not None
        assert points3d.shape[1] == 3
        points2d = self._camera.project_points(points3d)
        if clamp_to_screen:
            points2d = np.clip(points2d, 0, np.array(self.image.shape[:2])[::-1])
        self.draw_points(points2d, color=color, size=size)



    def draw_3d_line(self, point0: np.ndarray, point1: np.ndarray, color: Tuple[int, int, int] = (255, 255, 0), lw=1) -> None:
        assert self.image is not None
        assert point0.shape == point1.shape == (3,)
        points3d = np.vstack([point0, point1])
        points2d = self._camera.project_points(points3d)
        pt0 = self._convert_pt(points2d[0])
        pt1 = self._convert_pt(points2d[1])

    def draw_model_axes(self, face: Face, length: float, lw: int = 2) -> None:
        assert self.image is not None
        assert face is not None
        assert face.head_pose_rot is not None
        assert face.head_position is not None
        assert face.landmarks is not None
        # Get the axes of the model coordinate system
        axes3d = np.eye(3, dtype=np.float32) @ Rotation.from_euler("XYZ", [0, np.pi, 0]).as_matrix()
        axes3d = axes3d * length
        axes2d = self._camera.project_points(axes3d, face.head_pose_rot.as_rotvec(), face.head_position)
        center = face.landmarks[self._center_point_index]
        center = self._convert_pt(center)
        for pt, color in zip(axes2d, AXIS_COLORS):
            pt = self._convert_pt(pt)
            cv2.line(self.image, center, pt, color, lw, cv2.LINE_AA)

    def add_text(
        self, text: str, position: Tuple[int, int, int], color: Tuple[int, int, int] = (100, 200, 200), font_scale: float = 1
    ) -> None:
        assert self.image is not None

        # Ensure the position is a 2D point (x, y)
        if len(position) == 3:
            position = (int(position[0]), int(position[1]))

        cv2.putText(self.image, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 2, cv2.LINE_AA)

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

    def get_2d_resolution(self) -> Tuple[int, int]:
        assert self.image is not None
        return self.image.shape[:2]

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

    def create_opacity(self, overlay: np.ndarray, opacity: float):
        """
        Blends the original image and the overlay together, with a specified transparency/opacity
        """
        cv2.addWeighted(overlay, opacity, self.image, 1 - opacity, 0, self.image)

    def draw_labelled_rectangle(
        self,
        overlay: np.ndarray,
        top_left: Tuple[int, int],
        bottom_right: Tuple[int, int],
        color: Tuple[int, int, int],
        alpha: float,
        text: str,
        text_org: Tuple[int, int],
        text_font_face: int,
        text_line_type: int,
    ):
        """
        Draws a labelled rectangle on the specified overlay
        """
        cv2.rectangle(overlay, top_left, bottom_right, color, -1)
        self.create_opacity(overlay, alpha)
        cv2.putText(self.image, text, text_org, text_font_face, 1, color, 2, text_line_type, False)

    def calculate_rectangle_boundaries(self, width_max: int) -> Tuple[int, int, int]:
        """
        Calculates the left/right boundaries and the width of the boundaries, based on the maximum width of the image
        """
        middle_width = width_max / 2
        boundary_width = int(middle_width / 2)
        left_boundary = int(middle_width + boundary_width)
        right_boundary = int(boundary_width)
        return (left_boundary, right_boundary, boundary_width)

    def draw_bounds(self, points: np.ndarray, color: Tuple[int, int, int]):
        """
        Draws the left and right bounds depending where the user's gaze is
        """
        assert self.image is not None

        text_front_face = cv2.FONT_HERSHEY_SIMPLEX
        text_line_type = cv2.LINE_AA
        overlay = np.zeros_like(self.image, np.uint8)
        alpha = 0.3
        height_max = self.image.shape[0]
        width_max = self.image.shape[1]
        left_boundary, right_boundary, boundary_width = self.calculate_rectangle_boundaries(width_max)

        if points[0][0] >= left_boundary:
            top_left = (width_max, 0)
            bottom_right = (left_boundary, height_max)
            text = "Looking left"
            text_org = (1250, height_max // 2)
            # text_org = (left_boundary + boundary_width, height_max//2)
            self.draw_labelled_rectangle(overlay, top_left, bottom_right, color, alpha, text, text_org, text_front_face, text_line_type)

        elif points[0][0] <= right_boundary:
            top_left = (right_boundary, 0)
            bottom_right = (0, height_max)
            text = "Looking right"
            text_org = (50, height_max // 2)
            # text_org = (right_boundary - boundary_width//2, height_max//2)
            self.draw_labelled_rectangle(overlay, top_left, bottom_right, color, alpha, text, text_org, text_front_face, text_line_type)

    def draw_3d_point(
        self, point3d: np.ndarray, color: Tuple[int, int, int] = (255, 0, 255), size=3, clamp_to_screen: bool = False
    ) -> Tuple[int, int]:
        """
        Draw a point from 3D world coordinates onto the image.
        """
        assert self.image is not None
        assert point3d.shape == (3,)
        point2d = self._camera.project_point(point3d)
        if clamp_to_screen:
            point2d = self._clamp_point(point2d)
        self.draw_points(point2d[np.newaxis], color=color, size=size)
        return point2d

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
            points2d = self._clamp_point(points2d)
        self.draw_points(points2d, color=color, size=size)

    def draw_3d_line(self, point0: np.ndarray, point1: np.ndarray, color: Tuple[int, int, int] = (255, 255, 0), lw=1) -> None:
        assert self.image is not None
        assert point0.shape == point1.shape == (3,)
        points3d = np.vstack([point0, point1])
        points2d = self._camera.project_points(points3d)
        pt0 = self._convert_pt(points2d[0])
        pt1 = self._convert_pt(points2d[1])
        cv2.line(self.image, pt0, pt1, color, lw, cv2.LINE_AA)

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

    def _clamp_point(self, point_or_points: np.ndarray) -> np.ndarray:
        """
        Clamp the point or points to the image resolution
        """
        return np.clip(point_or_points, 0, np.array(self.image.shape[:2])[::-1])


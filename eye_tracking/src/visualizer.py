from typing import Optional, Tuple

import cv2
import numpy as np
from scipy.spatial.transform import Rotation
import logging

from camera import Camera
from face import Face
from utils import transforms

logger = logging.getLogger(__name__)
AXIS_COLORS = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]


class Visualizer:
    def __init__(self, camera: Camera, center_point_index: int):
        logger.info("Initialising Visualizer")
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
        :param overlay: The overlay to be blended with the original image
        :param opacity: The transparency of the overlay
        :return: None
        """

        img = np.zeros_like(self.image, np.uint8)
        cv2.addWeighted(overlay, opacity, self.image, 1 - opacity, 0, img)
        self.set_image(img)

    def calculate_text_org(
        self,
        text: str,
        text_font_face: int,
        font_scale: float,
        thickness: int,
        top_left: Tuple[int, int],
        bottom_right: Tuple[int, int],
    ):
        """
        Calculates the origin of the text to be drawn in the centre of the rectangle
        :param text: The text to be drawn
        :param text_font_face: The font face of the text
        :param font_scale: The scale of the font
        :param thickness: The thickness of the text
        :param top_left: The top left corner of the rectangle
        :param bottom_right: The bottom right corner of the rectangle
        :return: The origin of the text
        """

        (text_width, text_height), text_bottom_y = cv2.getTextSize(text, text_font_face, font_scale, thickness)
        text_middle = text_width // 2

        # Calculate the x_coordinate of the middle of the rectangle (i.e left-most x-coord of rectangle + middle of rectangle)
        rectangle_middle = (bottom_right[0] - top_left[0]) // 2
        rectangle_middle_x_coord = top_left[0] + rectangle_middle

        # Aligns the centre of the text with the centre of the rectangle
        rectangle_bottom_left = rectangle_middle_x_coord - text_middle
        text_org = (rectangle_bottom_left, (top_left[1] + bottom_right[1]) // 2)

        return text_org

    def draw_labelled_rectangle(
        self,
        top_left: Tuple[int, int],
        bottom_right: Tuple[int, int],
        bg_color: Tuple[int, int, int],
        bg_alpha: float,
        text: str,
        text_font_face: int = cv2.FONT_HERSHEY_SIMPLEX,
        text_line_type: int = cv2.LINE_AA,
        font_scale: float = 1.0,
        border_color: Optional[Tuple[int, int, int]] = None,
        border_thickness: int = 2,
        text_org: Optional[Tuple[int, int]] = None,
    ):
        """
        Draws a labelled rectangle on the specified overlay
        :param top_left: The top left corner of the rectangle
        :param bottom_right: The bottom right corner of the rectangle
        :param bg_color: The background colour of the rectangle
        :param bg_alpha: The transparency of the rectangle
        :param text: The text to be displayed
        :param text_font_face: The font face of the text
        :param text_line_type: The line type of the text
        :param font_scale: The scale of the font
        :param border_color: The colour of the border
        :param border_thickness: The thickness of the border
        :param text_org: The origin of the text
        :return: None
        """

        assert self.image is not None
        text_org = self.calculate_text_org(text, text_font_face, font_scale, 2, top_left, bottom_right)
        overlay = np.zeros_like(self.image, np.uint8)
        if border_color is not None:
            cv2.rectangle(overlay, top_left, bottom_right, border_color, -1)

            # Insets the rectangle to create a border effect
            top_left = transforms.add_2d_point(top_left, (border_thickness, border_thickness))
            bottom_right = transforms.add_2d_point(bottom_right, (-border_thickness, -border_thickness))

        cv2.rectangle(overlay, top_left, bottom_right, bg_color, -1)
        self.create_opacity(overlay, bg_alpha)
        cv2.putText(self.image, text, text_org, text_font_face, font_scale, bg_color, 2, text_line_type, False)

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

    def flip_point_x(self, point: Tuple[int, int]) -> Tuple[int, int]:
        """
        Flip the x-coordinate of the point
        """
        _, res_x = self.get_2d_resolution()
        flipped_point = point
        flipped_point[0] = res_x - flipped_point[0]
        return flipped_point

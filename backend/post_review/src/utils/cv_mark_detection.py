"""
OpenCV-based diagonal/cross mark detection utilities.

Used to detect handwritten diagonal/cross deletion marks while leaving
handwriting text interpretation to AI.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image

try:
    import cv2
except Exception:
    cv2 = None


def _to_grayscale(image: Image.Image) -> np.ndarray:
    image_array = np.array(image)
    if image_array.ndim == 3:
        return cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    return image_array


def detect_diagonal_cross(image: Image.Image) -> Dict[str, Any]:
    """Detect diagonal/cross handwritten marks in an image region."""
    default_result: Dict[str, Any] = {
        "has_diagonal_cross": False,
        "mark_type": "none",
        "confidence": 0.0,
        "line_count": 0,
        "debug": {"angles": [], "lengths": []},
    }

    if cv2 is None or image is None:
        return default_result

    try:
        gray = _to_grayscale(image)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 28, 95)

        height, width = edges.shape
        diagonal_length = float((width**2 + height**2) ** 0.5)

        passes = [
            {"min_ratio": 0.16, "threshold": 42, "max_gap": 22},
            {"min_ratio": 0.10, "threshold": 30, "max_gap": 30},
            {"min_ratio": 0.08, "threshold": 24, "max_gap": 34},
            {"min_ratio": 0.06, "threshold": 18, "max_gap": 38},
        ]

        positive_angles: List[float] = []
        negative_angles: List[float] = []
        lengths: List[float] = []

        for params in passes:
            min_line_length = max(8, int(diagonal_length * params["min_ratio"]))
            lines = cv2.HoughLinesP(
                edges,
                rho=1,
                theta=np.pi / 180,
                threshold=params["threshold"],
                minLineLength=min_line_length,
                maxLineGap=params["max_gap"],
            )

            if lines is None:
                continue

            for line in lines:
                x1, y1, x2, y2 = line[0]
                dx = x2 - x1
                dy = y2 - y1
                length = float((dx**2 + dy**2) ** 0.5)
                if length < min_line_length:
                    continue

                angle = abs(float(np.degrees(np.arctan2(dy, dx)))) % 180

                mid_x = (x1 + x2) / 2.0
                mid_y = (y1 + y2) / 2.0
                if not (0.10 * width <= mid_x <= 0.90 * width and 0.10 * height <= mid_y <= 0.90 * height):
                    continue

                if 20 <= angle <= 70:
                    positive_angles.append(angle)
                    lengths.append(length)
                elif 110 <= angle <= 160:
                    negative_angles.append(angle)
                    lengths.append(length)

        line_count = len(lengths)
        has_marks = line_count > 0

        if len(positive_angles) > 0 and len(negative_angles) > 0:
            mark_type = "cross"
        elif has_marks:
            mark_type = "diagonal"
        else:
            mark_type = "none"

        confidence = min(1.0, 0.25 + (line_count * 0.2)) if has_marks else 0.0

        return {
            "has_diagonal_cross": has_marks,
            "mark_type": mark_type,
            "confidence": confidence,
            "line_count": line_count,
            "debug": {
                "angles": [*positive_angles, *negative_angles],
                "lengths": lengths,
            },
        }
    except Exception:
        return default_result


def split_left_right_regions(image: Image.Image, split_ratio: float = 0.5) -> Dict[str, Tuple[int, int, int, int]]:
    """Return left/right rectangular regions for two-box section layouts."""
    width, height = image.size
    split_x = int(width * split_ratio)
    return {
        "left": (0, 0, split_x, height),
        "right": (split_x, 0, width, height),
    }


def detect_diagonal_cross_in_regions(
    image: Image.Image,
    regions: Dict[str, Tuple[int, int, int, int]],
) -> Dict[str, Dict[str, Any]]:
    """Detect diagonal/cross marks in named image regions."""
    results: Dict[str, Dict[str, Any]] = {}
    width, height = image.size

    for name, (x1, y1, x2, y2) in regions.items():
        left = max(0, min(width, int(x1)))
        top = max(0, min(height, int(y1)))
        right = max(0, min(width, int(x2)))
        bottom = max(0, min(height, int(y2)))

        if right <= left or bottom <= top:
            results[name] = {
                "has_diagonal_cross": False,
                "mark_type": "none",
                "confidence": 0.0,
                "line_count": 0,
                "debug": {"angles": [], "lengths": []},
            }
            continue

        cropped = image.crop((left, top, right, bottom))
        results[name] = detect_diagonal_cross(cropped)

    return results

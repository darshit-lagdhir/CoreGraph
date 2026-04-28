import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class AdaptiveLayoutManager:
    """
    SECTOR ZETA: Adaptive Layout Manager.
    Calculates character-grid dimensions in real-time for Full-Fit sovereignty.
    """

    def __init__(self, screen_width: int = 120, screen_height: int = 40):
        self.width = screen_width
        self.height = screen_height
        # Geometric Correction Factor (Sector Zeta)
        # Terminal cells are approx 2:1 height-to-width ratio.
        self.aspect_correction = 2.1

    def update_dimensions(self, width: int, height: int):
        self.width = width
        self.height = height
        logger.info(f"[Zeta] Layout Recalibrated: {width}x{height}")

    def get_full_fit_matrix(self) -> Tuple[int, int]:
        """Returns the optimized matrix dimensions for the terminal grid."""
        return (self.width, self.height)

    def calculate_spectral_coordinates(self, x: float, y: float) -> Tuple[int, int]:
        """
        Sector Zeta: Aspect-Ratio Normalization.
        Maps 0.0-1.0 coordinates to terminal grid cells with geometric correction.
        """
        norm_x = int(x * self.width)
        norm_y = int(y * self.height / self.aspect_correction)
        return (norm_x, norm_y)

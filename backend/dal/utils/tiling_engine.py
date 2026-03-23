import numpy as np
import msgpack
from typing import List, Dict, Any, Optional


class Box:
    """AABB: Axis-Aligned Bounding Box for graph spatial partitioning."""

    def __init__(self, min_x, max_x, min_y, max_y, min_z, max_z):
        self.min_x, self.max_x = min_x, max_x
        self.min_y, self.max_y = min_y, max_y
        self.min_z, self.max_z = min_z, max_z

    def contains(self, x, y, z) -> bool:
        return (
            self.min_x <= x <= self.max_x
            and self.min_y <= y <= self.max_y
            and self.min_z <= z <= self.max_z
        )


class OctreeNode:
    """
    High-fidelity spatial logic kernel.
    Recursive subdivision of 4M node clusters for multi-scale telemetry.
    """

    def __init__(self, boundary: Box, capacity: int = 500):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []  # Each entry: (x, y, z, id, weight, risk)
        self.children: Optional[List["OctreeNode"]] = None

    def insert(self, x, y, z, node_id, weight, risk) -> bool:
        if not self.boundary.contains(x, y, z):
            return False

        if len(self.points) < self.capacity and self.children is None:
            self.points.append((x, y, z, str(node_id), weight, risk))
            return True

        if self.children is None:
            self.subdivide()

        for child in self.children:
            if child.insert(x, y, z, node_id, weight, risk):
                return True
        return False

    def subdivide(self):
        """Splits the current Octant into 8 sub-octants."""
        b = self.boundary
        mid_x = (b.min_x + b.max_x) / 2
        mid_y = (b.min_y + b.max_y) / 2
        mid_z = (b.min_z + b.max_z) / 2

        self.children = [
            OctreeNode(Box(b.min_x, mid_x, b.min_y, mid_y, b.min_z, mid_z)),
            OctreeNode(Box(mid_x, b.max_x, b.min_y, mid_y, b.min_z, mid_z)),
            OctreeNode(Box(b.min_x, mid_x, mid_y, b.max_y, b.min_z, mid_z)),
            OctreeNode(Box(mid_x, b.max_x, mid_y, b.max_y, b.min_z, mid_z)),
            OctreeNode(Box(b.min_x, mid_x, b.min_y, mid_y, mid_z, b.max_z)),
            OctreeNode(Box(mid_x, b.max_x, b.min_y, mid_y, mid_z, b.max_z)),
            OctreeNode(Box(b.min_x, mid_x, mid_y, b.max_y, mid_z, b.max_z)),
            OctreeNode(Box(mid_x, b.max_x, mid_y, b.max_y, mid_z, b.max_z)),
        ]

        # Migrate existing points
        for p in self.points:
            for child in self.children:
                if child.insert(*p):
                    break
        self.points = []

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calculates semantic clumping aggregates for the current Octant."""
        all_pts = []
        if self.children:
            for child in self.children:
                metrics = child.get_summary_metrics()
                all_pts.extend(
                    [(metrics["x"], metrics["y"], metrics["z"], None, metrics["w"], metrics["r"])]
                )
        else:
            all_pts = self.points

        if not all_pts:
            return {"x": 0, "y": 0, "z": 0, "w": 0, "r": 0, "count": 0}

        pts_arr = np.array(all_pts, dtype=object)
        weights = pts_arr[:, 4].astype(float)
        risk_scores = pts_arr[:, 5].astype(float)
        total_w = np.sum(weights)

        center_x = np.sum(pts_arr[:, 0].astype(float) * weights) / total_w
        center_y = np.sum(pts_arr[:, 1].astype(float) * weights) / total_w
        center_z = np.sum(pts_arr[:, 2].astype(float) * weights) / total_w

        avg_risk = np.sum(risk_scores * weights) / total_w

        return {
            "x": float(center_x),
            "y": float(center_y),
            "z": float(center_z),
            "w": float(total_w),
            "r": float(avg_risk),
            "count": len(all_pts),
        }

    def serialize_tile(self) -> bytes:
        """Encodes spatial data into MessagePack for NVMe-optimized streaming."""
        payload = {
            "min": [self.boundary.min_x, self.boundary.min_y, self.boundary.min_z],
            "max": [self.boundary.max_x, self.boundary.max_y, self.boundary.max_z],
            "points": self.points if not self.children else [],
        }
        return msgpack.packb(payload)

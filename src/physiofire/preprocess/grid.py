"""Regular lat/lon grid aligned with the study region."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Grid:
    lon_min: float
    lat_min: float
    lon_max: float
    lat_max: float
    res: float

    @property
    def nx(self) -> int:
        return int(round((self.lon_max - self.lon_min) / self.res))

    @property
    def ny(self) -> int:
        return int(round((self.lat_max - self.lat_min) / self.res))

    @property
    def lon(self) -> np.ndarray:
        """Cell centres, west to east."""
        return self.lon_min + self.res * (np.arange(self.nx) + 0.5)

    @property
    def lat(self) -> np.ndarray:
        """Cell centres, south to north."""
        return self.lat_min + self.res * (np.arange(self.ny) + 0.5)

    def cell_index(self, lon: np.ndarray, lat: np.ndarray) -> np.ndarray:
        """Flat cell index (iy * nx + ix) for each point; -1 outside the grid."""
        ix = np.floor((lon - self.lon_min) / self.res).astype(np.int64)
        iy = np.floor((lat - self.lat_min) / self.res).astype(np.int64)
        inside = (ix >= 0) & (ix < self.nx) & (iy >= 0) & (iy < self.ny)
        return np.where(inside, iy * self.nx + ix, -1)


def grid_from_config(cfg: dict, name: str) -> Grid:
    r = cfg["region"]
    return Grid(r["lon_min"], r["lat_min"], r["lon_max"], r["lat_max"],
                float(cfg["grids"][name]["resolution_deg"]))

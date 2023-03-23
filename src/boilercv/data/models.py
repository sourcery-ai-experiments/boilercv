"""Models for image processing."""

from dataclasses import dataclass

import xarray as xr

from boilercv.types import SupportsMul


@dataclass
class UnitScale:
    """A unit scale."""

    dim: str
    """Coordinate dimension along which this scale applies."""
    long_name: str = ""
    """Long name which will show up in axis labels."""

    coords: SupportsMul | None = None
    """Coordinate values."""
    units: str = ""
    """Units."""

    original_units: str = ""
    """Original units to be converted from."""
    original_coords: SupportsMul | None = None
    """Original coordinate values to be converted from."""
    scale: float = 1
    """Scale factor to multiply the original coordinates by."""

    parent_dim: str = ""
    """Existing coordinate dimension to add these coordinates to."""

    @property
    def coordinate_units_match(self):
        """Whether the coordinate units are in the desired units."""
        return self.original_units == self.units

    def __post_init__(self):
        """Assign original units to units, and long name to dim, if not specified."""
        if self.units and not self.original_units:
            self.original_units = self.units
        if not self.long_name:
            self.long_name = self.dim.capitalize() if len(self.dim) > 1 else self.dim
        if not self.parent_dim:
            self.parent_dim = self.dim

    def assign_to(self, da: xr.DataArray):
        """Assign this scale to a coordinate."""
        if self.coords is None and self.dim == self.parent_dim:
            self.coords = da[self.parent_dim].values
        if not self.coordinate_units_match:
            self.convert()
        da = da.assign_coords({self.dim: (self.parent_dim, self.coords)})
        attrs = {"long_name": self.long_name}
        if self.units:
            attrs["units"] = self.units
        da[self.dim] = da[self.dim].assign_attrs(attrs)
        return da

    def convert(self):
        """Convert the original coordinates to the desired units."""
        if self.original_coords is not None:
            self.coords = self.original_coords * self.scale
        self.original_units = self.units
        self.original_coords = self.coords

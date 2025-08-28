# Geosquare Grid

Geosquare Grid is a Python library that provides methods for converting between geographic coordinates (longitude and latitude) and grid identifiers (GIDs). It also includes functionality for spatial operations and geometry handling, making it a useful tool for geospatial analysis and mapping applications.

## Features

- Convert longitude/latitude to GID and vice versa.
- Retrieve bounds for grid cells.
- Get geometries for grid cells.
- Find all grid cells that overlap with specified geometries.
- Easy integration with QGIS for geospatial applications.

## Installation

You can install the Geosquare Grid library using pip:

```bash
pip install geosquare-grid
```

## Usage

Here is a simple example of how to use the Geosquare Grid library:

```python
from geosquare_grid import GeosquareGrid

# Initialize the GeosquareGrid object
grid = GeosquareGrid()

# Convert longitude and latitude to GID
gid = grid.lonlat_to_gid(longitude=106.8938638928753022, latitude=-6.2608983083383016, level=5)
print(f"GID: {gid}")

# Convert GID back to longitude and latitude
longitude, latitude = grid.gid_to_lonlat(gid)
print(f"Longitude: {longitude}, Latitude: {latitude}")

# Get bounds for the grid cell
bounds = grid.get_bounds()
print(f"Bounds: {bounds}")
```

## Methods

### `lonlat_to_gid`
Converts geographic coordinates to a geospatial grid identifier (GID).

**Parameters:**
- `longitude` (float): Longitude in decimal degrees (-180 to 180).
- `latitude` (float): Latitude in decimal degrees (-90 to 90).
- `level` (int): Precision level (1-14).

**Returns:**
- `str`: Grid identifier.

---

### `gid_to_lonlat`
Converts a grid ID to geographic coordinates.

**Parameters:**
- `gid` (str): Grid identifier.

**Returns:**
- `Tuple[float, float]`: Longitude and latitude of the grid cell's lower-left corner.

---

### `gid_to_bound`
Converts a grid ID to its geographical bounds.

**Parameters:**
- `gid` (str): Grid identifier.

**Returns:**
- `Tuple[float, float, float, float]`: Bounding box `(min_longitude, min_latitude, max_longitude, max_latitude)`.

---

### `get_bounds`
Returns the geographic boundary of the grid cell.

**Returns:**
- `Tuple[float, float, float, float]`: Bounding box `(min_longitude, min_latitude, max_longitude, max_latitude)`.

---

### `polyfill`
Finds all grid cells that intersect with a polygon.

**Parameters:**
- `geometry` (Polygon): Polygon geometry to fill.
- `size` (Union[int, List[int]]): Grid cell size or range of sizes.
- `start` (str): Starting cell identifier (default: "2").
- `fullcover` (bool): If `True`, only fully contained cells are returned.

**Returns:**
- `List[str]`: List of grid cell identifiers.

## Grid Cell Resolution Reference

| Size (meter) | Level | Approximate Cell Dimensions |
|----------|-------|----------------------------|
| 10000000 | 1     | Country-sized              |
| 1000000  | 3     | Large region               |
| 100000   | 5     | City-sized                 |
| 10000    | 7     | Neighborhood               |
| 5000     | 8     | Block-sized                |
| 1000     | 9     | Block-sized                |
| 500      | 10    | Large building             |
| 100      | 11    | Building complex           |
| 50       | 12    | Building                   |
| 10       | 13    | Building                   |
| 5        | 14    | Room-sized                 |

## Documentation

For more detailed documentation, including advanced usage and API reference, please refer to the [docs](docs/index.rst).

## Versioning

This project uses automatic versioning based on Git tags with [setuptools_scm](https://github.com/pypa/setuptools_scm/). 

### How it works:
- The version is automatically determined from Git tags
- Development versions include the commit hash (e.g., `1.0.0.dev0+g1234567`)
- Release versions match the Git tag exactly (e.g., `1.0.0`)

### Creating a new release:
1. Create and push a Git tag:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin --tags
   ```
2. The GitHub Actions workflow will automatically build and publish to PyPI when a release is created

### Version management script:
Use the included script for version management:
```bash
# Show current version
python scripts/version_manager.py --current

# Create a new tag
python scripts/version_manager.py --create-tag v1.0.0 --message "Release version 1.0.0"
```

## License

This project is licensed under the GPL-3.0 license. See the [LICENSE](LICENSE) file for more details.

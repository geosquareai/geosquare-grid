GeosquareGrid
=============

A flexible geospatial grid system for location encoding and spatial operations.

GeosquareGrid implements a hierarchical grid system that encodes geographic locations
into compact string identifiers (GIDs) and provides various spatial operations.

The grid divides the world into cells of varying resolution levels (1-15), where
each level increases the precision of location representation.

Installation
------------

To install the `GeosquareGrid` library, use pip:

.. code-block:: bash

    pip install geosquare-grid

Alternatively, you can install it directly from the source:

.. code-block:: bash

    git clone https://github.com/your-repo/geosquare-grid.git
    cd geosquare-grid
    pip install .

Key Features
------------

- Convert between geographic coordinates (longitude, latitude) and grid identifiers
- Support for multiple resolution levels (1-15) with cell sizes from ~10,000km to ~1m
- Generate boundary geometries for grid cells
- Perform spatial operations like retrieving parent/child cells
- Fill arbitrary polygons with grid cells at specified resolutions

Examples
--------

Creating a grid from coordinates:

.. code-block:: python

    >>> grid = GeosquareGrid()
    >>> grid.from_lonlat(longitude=106.894082, latitude=-6.26109, level=7)
    >>> grid.gid
    'J3N2M3T8M342'

Converting between formats:

.. code-block:: python

    >>> grid = GeosquareGrid()
    >>> gid = grid.lonlat_to_gid(106.894082, -6.26109, 5)
    >>> lon, lat = grid.gid_to_lonlat(gid)

Finding grid cells that cover a polygon:

.. code-block:: python

    >>> grid = GeosquareGrid()
    >>> from shapely.geometry import Polygon
    >>> poly = Polygon([(106.82, -6.86), (106.892, -6.86), (106.82, -7), (106.89, -7)])
    >>> cells = grid.polyfill(poly, size=1000)

Function Usage
--------------

1. **from_lonlat**: Initialize a grid cell from longitude, latitude, and level.

.. code-block:: python

    >>> grid = GeosquareGrid()
    >>> grid.from_lonlat(longitude=106.894082, latitude=-6.26109, level=7)
    >>> grid.gid
    'J3N2M3T8M342'

2. **from_gid**: Initialize a grid cell from a grid ID (GID).

.. code-block:: python

    >>> grid = GeosquareGrid()
    >>> grid.from_gid("J3N2M3T8M342")
    >>> grid.longitude, grid.latitude
    (106.894082, -6.26109)

3. **lonlat_to_gid**: Convert longitude, latitude, and level to a grid ID.

.. code-block:: python

    >>> grid = GeosquareGrid()
    >>> gid = grid.lonlat_to_gid(106.894082, -6.26109, 7)
    >>> gid
    'J3N2M3T8M342'

4. **gid_to_lonlat**: Convert a grid ID to longitude and latitude.

.. code-block:: python

    >>> grid = GeosquareGrid()
    >>> lon, lat = grid.gid_to_lonlat("J3N2M3T8M342")
    >>> lon, lat
    (106.894082, -6.26109)

5. **gid_to_bound**: Get the bounding box of a grid cell.

.. code-block:: python

    >>> grid = GeosquareGrid()
    >>> bounds = grid.gid_to_bound("J3N2M3T8M342")
    >>> bounds
    (106.8938638928753022,-6.2613474659803572, 106.8943130505173542,-6.2608983083383016)

6. **polyfill**: Find all grid cells that intersect with a polygon.

.. code-block:: python

    >>> grid = GeosquareGrid()
    >>> from shapely.geometry import Polygon
    >>> poly = Polygon([(106.8938638928753022, -6.2613474659803572), (106.8943130505173542, -6.2613474659803572), (106.8943130505173542, -6.2608983083383016), (106.8938638928753022, -6.2608983083383016)])
    >>> cells = grid.polyfill(poly, size=50)
    >>> cells
    ['J3N2M3T8M342', 'J3N2M3T8M343', ...]

7. **get_geometry**: Get the polygon geometry of a grid cell.

.. code-block:: python

    >>> grid = GeosquareGrid()
    >>> grid.from_gid("J3N2M3T8M342")
    >>> geometry = grid.get_geometry()
    >>> geometry
    <shapely.geometry.polygon.Polygon object at 0x...>

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

Notes
-----

- The grid system uses a custom 25-character encoding alphabet organized in a 5x5 matrix
- Longitude must be between -180 and 180 degrees
- Latitude must be between -90 and 90 degrees
- Resolution levels must be between 1 and 14

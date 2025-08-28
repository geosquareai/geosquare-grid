from typing import List, Tuple, Union

from shapely import intersection, wkt
from shapely.geometry import Polygon

class GeosquareGrid:
    """"
    GeosquareGrid
    ---------------
    A flexible geospatial grid system for location encoding and spatial operations.
    GeosquareGrid implements a hierarchical grid system that encodes geographic locations
    into compact string identifiers (GIDs) and provides various spatial operations.
    The grid divides the world into cells of varying resolution levels (1-15), where
    each level increases the precision of location representation.
    Key Features
    -----------
    - Convert between geographic coordinates (longitude, latitude) and grid identifiers
    - Support for multiple resolution levels (1-15) with cell sizes from ~10,000km to ~1m
    - Generate boundary geometries for grid cells
    - Perform spatial operations like retrieving parent/child cells
    - Fill arbitrary polygons with grid cells at specified resolutions
    Creating a grid from coordinates:
        >>> grid = GeosquareGrid()
        >>> grid.from_lonlat(longitude=121.5, latitude=31.2, level=7)
        >>> grid.gid
        'WXYZPRG'
    Converting between formats:
        >>> grid = GeosquareGrid()
        >>> gid = grid.lonlat_to_gid(121.5, 31.2, 5)
        >>> lon, lat = grid.gid_to_lonlat(gid)
    Finding grid cells that cover a polygon:
        >>> grid = GeosquareGrid()
        >>> from shapely.geometry import Polygon
        >>> poly = Polygon([(120, 30), (122, 30), (122, 32), (120, 32)])
        >>> cells = grid.polyfill(poly, size=1000)
    - The grid system uses a custom 25-character encoding alphabet organized in a 5x5 matrix
    - Longitude must be between -180 and 180 degrees
    - Latitude must be between -90 and 90 degrees
    - Resolution levels must be between 1 and 15
    - The grid system reference ranges are non-standard (-216 to 233.16 for latitude and 
      -217 to 232.16 for longitude) for internal calculations
    """
    def __init__(self):
        """
        Initialize a geospatial grid object.
        This constructor sets up the encoding infrastructure for the geographic grid system.
        When created, a grid object has no specific location until its coordinates are set.
        Attributes:
            longitude (float, optional): Longitude coordinate in decimal degrees.
            latitude (float, optional): Latitude coordinate in decimal degrees.
            level (int, optional): Resolution level of the grid.
            gid (str, optional): Grid identifier code.
            address (str, optional): Human-readable address corresponding to the location.
        The initialization also sets up the following encoding constants and lookup tables:
            - CODE_ALPHABET: A 5x5 matrix of alphanumeric characters used for encoding
            - CODE_ALPHABET_: Pre-computed flattened versions of the alphabet for different bases
            - CODE_ALPHABET_VALUE: Maps each character to its (row, column) position in the alphabet
            - CODE_ALPHABET_INDEX: Maps each character to its index position in the flattened alphabets
            - d: Base sizes for each position in the encoding
            - size_level: Maps geographic sizes (likely in meters) to corresponding grid levels
        """
        
        self.longitude = None
        self.latitude = None
        self.level = None
        self.gid = None
        self.address = None
        
        # Initialize constants
        self.CODE_ALPHABET = [
            ["2", "3", "4", "5", "6"],
            ["7", "8", "9", "C", "E"],
            ["F", "G", "H", "J", "L"],
            ["M", "N", "P", "Q", "R"],
            ["T", "V", "W", "X", "Y"],
        ]
        
        # Pre-compute derived constants for faster lookups
        self.CODE_ALPHABET_ = {
            5: sum(self.CODE_ALPHABET, []),
            2: sum([c[:2] for c in self.CODE_ALPHABET[:2]], []),
            "c2": ["2", "3"],
            "c12": ["V", "X", "N", "M", "F", "R", "P", "W", "H", "G", "Q", "L", "Y", "T", "J"],
        }
        
        self.CODE_ALPHABET_VALUE = {
            j: (idx_1, idx_2)
            for idx_1, i in enumerate(self.CODE_ALPHABET)
            for idx_2, j in enumerate(i)
        }
        
        self.CODE_ALPHABET_INDEX = {
            k: {val: idx for idx, val in enumerate(v)}
            for k, v in self.CODE_ALPHABET_.items()
        }
        
        self.d = [5, 2, 5, 2, 5, 2, 5, 2, 5, 2, 5, 2, 5, 2, 5]
        self.size_level = {
            10000000: 1, 5000000: 2, 1000000: 3, 500000: 4,
            100000: 5, 50000: 6, 10000: 7, 5000: 8,
            1000: 9, 500: 10, 100: 11, 50: 12,
            10: 13, 5: 14, 1: 15,
        }

    def lonlat_to_gid(self, longitude: float, latitude: float, level: int) -> str:
        """
        Convert geographic coordinates (longitude, latitude) to a geospatial grid identifier (GID).
        This method transforms coordinates into a string identifier representing a grid cell
        at the specified precision level. The grid system divides the world into increasingly
        fine cells as the level increases.
        Parameters
        ----------
        longitude : float
            The longitude coordinate in decimal degrees, must be between -180 and 180.
        latitude : float
            The latitude coordinate in decimal degrees, must be between -90 and 90.
        level : int
            The precision level of the grid cell, must be between 1 and 15.
            Higher levels result in smaller (more precise) grid cells.
        Returns
        -------
        str
            A string identifier representing the grid cell containing the provided coordinates.
            The length of the string equals the specified level.
        Raises
        ------
        AssertionError
            If the input coordinates or level are outside their valid ranges.
        Examples
        --------
        >>> grid.lonlat_to_gid(121.5, 31.2, 5)
        'WXYZP'
        """
        
        
        assert -180 <= longitude <= 180, "Longitude must be between -180 and 180"
        assert -90 <= latitude <= 90, "Latitude must be between -90 and 90"
        assert 1 <= level <= 15, "Level must be between 1 and 15"
        
        lat_ranged = (-216, 233.157642055036)
        lon_ranged = (-217, 232.157642055036)
        gid = ""
        
        for part in self.d[:level]:
            position_x = int((longitude - lon_ranged[0]) / (lon_ranged[1] - lon_ranged[0]) * part)
            position_y = int((latitude - lat_ranged[0]) / (lat_ranged[1] - lat_ranged[0]) * part)
            
            part_x = (lon_ranged[1] - lon_ranged[0]) / part
            part_y = (lat_ranged[1] - lat_ranged[0]) / part
            
            shift_x = part_x * position_x
            shift_y = part_y * position_y
            
            lon_ranged = (lon_ranged[0] + shift_x, lon_ranged[0] + shift_x + part_x)
            lat_ranged = (lat_ranged[0] + shift_y, lat_ranged[0] + shift_y + part_y)
            
            gid += self.CODE_ALPHABET[position_y][position_x]
            
        return gid

    def gid_to_lonlat(self, gid: str) -> Tuple[float, float]:
        """
        Convert a grid ID (GID) to geographic coordinates (longitude, latitude).
        This method decodes a grid ID string into the corresponding geographic coordinates
        by progressively narrowing down coordinate ranges based on each character in the GID.
        Each character in the GID represents a specific position in the hierarchical grid system.
        Args:
            gid (str): The grid ID to convert.
        Returns:
            Tuple[float, float]: A tuple containing (longitude, latitude) coordinates
            corresponding to the lower-left corner of the grid cell.
        Example:
            >>> grid.gid_to_lonlat("AB12")
            (23.45, 67.89)
        """
        
            
        lat_ranged = (-216, 233.157642055036)
        lon_ranged = (-217, 232.157642055036)
        
        for idx, char in enumerate(gid):
            part_x = (lon_ranged[1] - lon_ranged[0]) / self.d[idx]
            part_y = (lat_ranged[1] - lat_ranged[0]) / self.d[idx]
            
            shift_x = part_x * self.CODE_ALPHABET_VALUE[char][1]
            shift_y = part_y * self.CODE_ALPHABET_VALUE[char][0]
            
            lon_ranged = (lon_ranged[0] + shift_x, lon_ranged[0] + shift_x + part_x)
            lat_ranged = (lat_ranged[0] + shift_y, lat_ranged[0] + shift_y + part_y)
            
        result = (lon_ranged[0], lat_ranged[0])
        return result

    def gid_to_bound(self, gid: str) -> Tuple[float, float, float, float]:
        """
        Converts a grid identifier (gid) to geographical bounds.
        This method translates a geosquare grid identifier string to its corresponding
        geographical bounding box coordinates. The method iteratively processes each character
        in the gid to narrow down the geographical area from the initial range.
        Parameters
        ----------
        gid : str
            The grid identifier string to convert to geographical bounds.
        Returns
        -------
        Tuple[float, float, float, float]
            A tuple representing the bounding box as (min_longitude, min_latitude, max_longitude, max_latitude).
        Examples
        --------
        >>> grid.gid_to_bound("AB12")
        (-216.0, -216.0, -215.9, -215.9)  # Example values
        """
        
            
        lat_ranged = (-216, 233.157642055036)
        lon_ranged = (-217, 232.157642055036)
        
        for idx, char in enumerate(gid):
            part_x = (lon_ranged[1] - lon_ranged[0]) / self.d[idx]
            part_y = (lat_ranged[1] - lat_ranged[0]) / self.d[idx]
            
            shift_x = part_x * self.CODE_ALPHABET_VALUE[char][1]
            shift_y = part_y * self.CODE_ALPHABET_VALUE[char][0]
            
            lon_ranged = (lon_ranged[0] + shift_x, lon_ranged[0] + shift_x + part_x)
            lat_ranged = (lat_ranged[0] + shift_y, lat_ranged[0] + shift_y + part_y)
            
        result = (lon_ranged[0], lat_ranged[0], lon_ranged[1], lat_ranged[1])
        return result


    def from_lonlat(self, longitude: float, latitude: float, level: int) -> None:
        """
        Initialize grid cell from longitude, latitude, and level.
        Parameters
        ----------
        longitude : float
            Longitude coordinate in WGS84 (must be between -180 and 180).
        latitude : float
            Latitude coordinate in WGS84 (must be between -90 and 90).
        level : int
            Grid level/resolution (must be between 1 and 15).
        Returns
        -------
        None
            This method updates the object's attributes in-place.
        Notes
        -----
        This method sets the object's longitude, latitude, level attributes
        and calculates the corresponding grid ID (gid).
        """
        
        assert -180 <= longitude <= 180, "Longitude must be between -180 and 180"
        assert -90 <= latitude <= 90, "Latitude must be between -90 and 90"
        assert 1 <= level <= 15, "Level must be between 1 and 15"
        
        self.longitude = longitude
        self.latitude = latitude
        self.level = level
        self.gid = self.lonlat_to_gid(self.longitude, self.latitude, self.level)

    def from_gid(self, gid: str) -> None:
        """
        Initialize cell attributes from a grid ID (GID).
        This method sets the object properties based on a provided grid ID string.
        Args:
            gid (str): A string representing the grid ID.
        Returns:
            None
        Notes:
            This method sets the following instance attributes:
            - gid: The provided grid ID
            - level: The level/resolution of the cell (derived from GID length)
            - longitude: The longitude of the cell's center point
            - latitude: The latitude of the cell's center point
        """
        
        self.gid = gid
        self.level = len(gid)
        self.longitude, self.latitude = self.gid_to_lonlat(self.gid)

    def from_address(self, address: str) -> None:
        """
        Initialize the object from a given square address string.
        This method sets the address attribute and attempts to convert it to a grid ID
        using the address_to_gid method. If the address is not valid, an exception is raised.
        Args:
            address (str): The square address string to initialize the object with.
        Raises:
            ValueError: If the provided address is not valid.
        Returns:
            None
        """
        
        self.address = address
        if not self.address_to_gid():
            raise ValueError("Address is not valid")

    def get_gid(self) -> str:
        """
        Get the geographic identifier (GID) for this grid cell.
        Returns the pre-computed GID if available. Otherwise, calculates the GID
        from the instance's longitude, latitude, and level attributes using the
        lonlat_to_gid method.
        Returns:
            str: The geographic identifier (GID) for this grid cell.
        Raises:
            ValueError: If any of longitude, latitude, or level attributes are None
                        when trying to compute the GID.
        """
        
        if self.gid is None:
            if None in (self.longitude, self.latitude, self.level):
                raise ValueError("Cannot get GID without longitude, latitude, and level")
            self.gid = self.lonlat_to_gid(self.longitude, self.latitude, self.level)
        return self.gid

    def get_lonlat(self) -> Tuple[float, float]:
        """
        Get the longitude and latitude coordinates for this grid cell.
        If longitude and latitude aren't already set, attempts to derive them
        from the cell's GID (Grid Identifier) using the gid_to_lonlat conversion.
        Returns:
            Tuple[float, float]: A tuple containing (longitude, latitude)
        Raises:
            ValueError: If neither coordinates nor GID are available
        """
        
        if self.longitude is None or self.latitude is None:
            if self.gid is None:
                raise ValueError("Cannot get lon/lat without GID")
            self.longitude, self.latitude = self.gid_to_lonlat(self.gid)
        return self.longitude, self.latitude

    def get_bound(self) -> Tuple[float, float, float, float]:
        """
        Get the geographic boundary of the current grid cell.
        Returns:
            Tuple[float, float, float, float]: The bounding coordinates of the grid cell,
                typically in the format (min_longitude, min_latitude, max_longitude, max_latitude)
                or (west, south, east, north).
        """

        return self.gid_to_bound(self.gid)

    def get_geometry(self) -> Polygon:
        """
        Returns the polygon geometry of this grid cell.
        This method converts the current grid ID (gid) to its corresponding
        geometry representation by calling the `gid_to_geometry` method.
        Returns
        -------
        Polygon
            The polygon geometry representing the boundaries of this grid cell.
        """
        
        return self.gid_to_geometry(self.gid)

    def gid_to_geometry(self, gid: str) -> Polygon:
        """
        Converts a grid ID (gid) to its corresponding polygon geometry.
        This method translates a grid identifier into a geometric representation,
        by first converting it to Well-Known Text (WKT) format via an internal method,
        then parsing the WKT into a proper Polygon object.
        Args:
            gid (str): The grid identifier to convert to a geometry.
        Returns:
            Polygon: A polygon geometry representing the grid cell identified by the gid.
        """
        
        geom_wkt = self._gid_to_geometry_wkt(gid)
        result = wkt.loads(geom_wkt)
        return result

    def _gid_to_geometry_wkt(self, gid: str) -> str:
        """
        Convert a grid ID to a Well-Known Text (WKT) representation of its geometry.
        This method takes a grid ID and converts it to a polygon geometry in WKT format.
        It first gets the bounds of the grid cell using `gid_to_bound`, then constructs
        a WKT string representing a polygon with those bounds.
        Parameters
        ----------
        gid : str
            The grid ID to convert to geometry.
        Returns
        -------
        str
            WKT representation of the polygon geometry corresponding to the grid ID.
            Format: "Polygon ((x1 y1, x1 y2, x2 y2, x2 y1, x1 y1))"
        """

        a = self.gid_to_bound(gid)
        return (
            f"Polygon (({a[0]} {a[1]},{a[0]} {a[3]}," 
            f"{a[2]} {a[3]},{a[2]} {a[1]},{a[0]} {a[1]}))"
        )
    

    @staticmethod
    def _area_ratio(a, b) -> float:
        """
        Calculate the ratio of the intersection area between two shapes to the area of the first shape.
        Parameters:
        ----------
        a : geometry
            The first geometry object with an area property. The denominator in the ratio calculation.
        b : geometry
            The second geometry object with an area property. Used to calculate the intersection.
        Returns:
        -------
        float
            The ratio of the intersection area to the area of 'a', rounded to 20 decimal places.
            Value ranges from 0.0 (no intersection) to 1.0 (complete containment of 'a' within 'b').
        Notes:
        -----
        This function relies on an 'intersection' function and objects that have an 'area' property.
        """

        return round(intersection(a, b).area / a.area, 20)


    # === Spatial operations ===

    def parrent_to_allchildren(self, key: str, size: int, geometry: Polygon = None) -> List[str]:
        """
        Generates all child grid identifiers (GIDs) at a specified resolution level from a parent GID.
        This method performs a breadth-first traversal to find all child cells at the target resolution level.
        If a geometry is provided, only child cells that intersect with the geometry are included in the results.
        Parameters:
        ----------
        key : str
            The parent grid identifier (GID).
        size : int
            The target size parameter which determines the resolution level of child cells.
        geometry : Polygon, optional
            A geometry to filter child cells. Only cells that intersect with this geometry will be included.
        Returns:
        -------
        List[str]
            A list of grid identifiers for all child cells at the specified resolution level that meet the
            geometry filter criteria (if a geometry is provided).
        Raises:
        ------
        ValueError
            If the target resolution is less than the parent's resolution.
        Notes:
        -----
        If the target resolution equals the parent's resolution, the method simply returns the parent key.
        """

        resolution = self.size_level[size]
        parrent_resolution = len(key) - resolution
        if resolution < parrent_resolution:
            raise ValueError("resolution must be less than or equal to the length of the GID")
        if resolution == parrent_resolution:
            return [key]
        keys = []
        queue = [key]
        while queue:
            current_key = queue.pop(0)
            if len(current_key) == resolution:
                if geometry is not None:
                    if self._area_ratio(self.gid_to_geometry(current_key), geometry) > 0:
                        keys.append(current_key)
                else:
                    keys.append(current_key)
            elif len(current_key) > resolution:
                break
            else:
                for child_key in self._to_children(current_key):
                    queue.append(child_key)

        return keys

    
    def _to_children(self, key: str) -> Tuple[str, ...]:
        """
        Convert a key to its child keys by appending characters from the code alphabet.
        This method generates all child keys for a given parent key by appending the appropriate 
        characters based on the current level in the hierarchy.
        Parameters
        ----------
        key : str
            The parent key string to generate children for
        Returns
        -------
        Tuple[str, ...]
            A tuple containing all child keys generated by appending characters
            from the appropriate alphabet to the parent key
        """
        
        return tuple(key + i for i in self.CODE_ALPHABET_[self.d[len(key)]])
    
    def _to_parent(self, key: str) -> str:
        """
        Convert a key to its parent key by removing the last character.
        If the key has only one character, return the key unchanged.
        Parameters:
            key (str): The key to convert to parent.
        Returns:
            str: The parent key.
        """
        
        return key[:-1] if len(key) > 1 else key

    def _get_contained_keys(
        self,
        geometry: Polygon,
        initial_key: str,
        resolution: List[int],
        fullcover: bool = True
    ) -> List[str]:
        
        """
        Find grid cell keys contained within a specified geometry.
        This method identifies all grid cells at the specified resolution that intersect
        with or are contained within the given geometry. It uses a recursive approach to
        efficiently search the geospatial grid hierarchy.
        Parameters
        ----------
        geometry : Polygon
            The geographic area to check for containment.
        initial_key : str
            The starting grid key to begin the search from.
        resolution : List[int]
            A list of [min_resolution, max_resolution] specifying the minimum and maximum
            key length (detail level) to include in the results.
        fullcover : bool, default True
            If True, only includes cells that are fully contained within the geometry.
            If False, also includes cells that are more than 50% covered by the geometry.
        Returns
        -------
        List[str]
            A list of grid cell keys that meet the containment criteria.
        Notes
        -----
        The method uses a depth-first recursive algorithm to explore the grid hierarchy.
        It calculates the area ratio between each cell and the input geometry to determine
        containment, and prunes the search when there is no overlap between a cell and 
        the target geometry.
        """
           
        if initial_key != "2":
            geometry = geometry.intersection(self.gid_to_geometry(initial_key))
        contained_keys = []
        def func(key, approved):
            if approved:
                if resolution[0] <= len(key) <= resolution[1]:
                    contained_keys.append(key)
                else:
                    for child_key in self._to_children(key):
                        func(child_key, True)
            else:
                area_ratio = self._area_ratio(
                    self.gid_to_geometry(key), geometry)
                if area_ratio == 0:
                    last_idx = self.CODE_ALPHABET_[self.d[0]].index(key[-1])
                    if (last_idx < 25) & (len(key) == 1):
                        func(
                            key[:-1] + self.CODE_ALPHABET_[self.d[0]
                                                           ][last_idx + 1][0],
                            False,
                        )
                    else:
                        return
                elif area_ratio == 1:
                    func(key, True)
                elif (len(key) == resolution[1]) & fullcover:
                    contained_keys.append(key)
                elif (len(key) == resolution[1]) & (area_ratio > 0.5) & (~fullcover):
                    contained_keys.append(key)
                elif len(key) == resolution[1]:
                    return
                else:
                    for child_key in self._to_children(key):
                        func(child_key, False)

        func(initial_key, False)
        return contained_keys

    def polyfill(
        self, 
        geometry: Polygon, 
        size: Union[int, List[int]], 
        start: str = "2", 
        fullcover: bool = True
    ) -> List[str]:
        """
        Find all grid cells that intersect with the given polygon geometry.
        Parameters
        ----------
        geometry : Polygon
            The polygon geometry to be filled with grid cells.
        size : Union[int, List[int]]
            If int: The size level of grid cells to use.
            If list: A range [min, max] of size levels to consider, where min > max 
            (smaller number means larger cell size).
        start : str, optional
            The starting cell identifier to begin the search from. Default is "2".
        fullcover : bool, optional
            If True, only returns cells that are fully contained within the geometry.
            If False, returns cells that intersect with the geometry. Default is True.
        Returns
        -------
        List[str]
            A list of grid cell identifiers that satisfy the containment criteria.
        Raises
        ------
        AssertionError
            If the size parameter contains invalid values or if the size list is not in [min, max] format.
        Notes
        -----
        The size parameter must correspond to valid keys in the 1 - 15 size level mapping.
        """
        if isinstance(size, list):
            assert size[0] > size[1], "size must be in [min, max] format"
            assert size[0] in self.size_level, f"size must be in {list(self.size_level.keys())}"
            assert size[1] in self.size_level, f"size must be in {list(self.size_level.keys())}"
            resolution = [self.size_level[i] for i in size]
        else:
            assert size in self.size_level, f"size must be in {list(self.size_level.keys())}"
            resolution = [self.size_level[size], self.size_level[size]]
            
        return self._get_contained_keys(
            geometry,
            start,
            resolution,
            fullcover
        )

    def __repr__(self) -> str:
        """String representation of the grid"""
        return f"PetainGrid(gid={self.gid}, address={self.address}, longitude={self.longitude}, latitude={self.latitude}, level={self.level})"
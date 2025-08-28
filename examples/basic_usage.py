# Contents of examples/basic_usage.py

from geosquare_grid.core import GeosquareGrid

def main():
    # Create an instance of GeosquareGrid
    grid = GeosquareGrid()

    # Example coordinates
    longitude = 106.894082
    latitude = -6.26109
    level = 12

    # Convert longitude/latitude to GID
    gid = grid.lonlat_to_gid(longitude, latitude, level)
    print(f"GID for coordinates ({longitude}, {latitude}) at level {level}: {gid}")

    # Convert GID back to longitude/latitude
    lon, lat = grid.gid_to_lonlat(gid)
    print(f"Coordinates for GID {gid}: ({lon}, {lat})")

    # Get bounds for the GID
    bounds = grid.gid_to_bound(gid)
    print(f"Bounds for GID {gid}: {bounds}")

if __name__ == "__main__":
    main()
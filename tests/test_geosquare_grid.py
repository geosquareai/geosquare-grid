import unittest
from src.geosquare_grid.core import GeosquareGrid

class TestGeosquareGrid(unittest.TestCase):

    def setUp(self):
        self.grid = GeosquareGrid()

    def test_indonesia_gid_remains_the_same(self):
        # Indonesia must NOT change algorithm
        # Original GID for Jakarta at level 14
        lon, lat = 106.894082, -6.26109
        gid = self.grid.lonlat_to_gid(lon, lat, 14)
        self.assertEqual(gid, "J3N2M3T8M342H7")

        dec_lon, dec_lat = self.grid.gid_to_lonlat(gid)
        self.assertAlmostEqual(dec_lon, 106.8940435559, places=5)
        self.assertAlmostEqual(dec_lat, -6.26112288715, places=5)

    def test_new_york_accurate_gid(self):
        # New York is outside Indonesia
        lon, lat = -74.006, 40.7128
        gid = self.grid.lonlat_to_gid(lon, lat, 14)
        # We don't know the exact new GID string yet, but we know it MUST start with a lowercase letter
        self.assertTrue(gid[0].islower())
        self.assertEqual(len(gid), 15) # 1 zone char + 14 grid chars

        dec_lon, dec_lat = self.grid.gid_to_lonlat(gid)
        # Should decode back to very close to the original coordinates
        self.assertAlmostEqual(dec_lon, lon, places=3)
        self.assertAlmostEqual(dec_lat, lat, places=3)

    def test_oslo_accurate_gid(self):
        # Oslo is outside Indonesia
        lon, lat = 10.762622, 59.911491
        gid = self.grid.lonlat_to_gid(lon, lat, 14)
        self.assertTrue(gid[0].islower())
        self.assertEqual(len(gid), 15)

        dec_lon, dec_lat = self.grid.gid_to_lonlat(gid)
        self.assertAlmostEqual(dec_lon, lon, places=3)
        self.assertAlmostEqual(dec_lat, lat, places=3)

    def test_lonlat_to_gid(self):
        gid = self.grid.lonlat_to_gid(106.894082, -6.26109, 14)
        self.assertEqual(gid, "J3N2M3T8M342H7")

    def test_gid_to_lonlat(self):
        lonlat = self.grid.gid_to_lonlat("J3N2M3T8M342H7")
        self.assertAlmostEqual(lonlat[0], 106.89404355593213, places=5)
        self.assertAlmostEqual(lonlat[1], -6.261122887159329, places=5)

    def test_gid_to_bound(self):
        bounds = self.grid.gid_to_bound("J3N2M3T8M342H7")
        # Ensure it returns a 4-element tuple
        self.assertEqual(len(bounds), 4)
        # Coordinates should wrap around the decoded point
        self.assertTrue(bounds[0] <= 106.89404355593213 <= bounds[2])
        self.assertTrue(bounds[1] <= -6.261122887159329 <= bounds[3])

    def test_from_lonlat(self):
        self.grid.from_lonlat(106.894082, -6.26109, 14)
        self.assertEqual(self.grid.gid, "J3N2M3T8M342H7")

    def test_from_gid(self):
        self.grid.from_gid("J3N2M3T8M342H7")
        self.assertAlmostEqual(self.grid.longitude, 106.89404355593213, places=5)
        self.assertAlmostEqual(self.grid.latitude, -6.261122887159329, places=5)

    def test_get_gid(self):
        self.grid.from_lonlat(106.894082, -6.26109, 5)
        self.assertEqual(self.grid.get_gid(), "J3N2M")

    def test_get_lonlat(self):
        self.grid.from_gid("J3N2M3T8M342H7")
        lonlat = self.grid.get_lonlat()
        self.assertAlmostEqual(lonlat[0], 106.89404355593213, places=5)
        self.assertAlmostEqual(lonlat[1], -6.261122887159329, places=5)

    def test_get_bound(self):
        self.grid.from_gid("J3N2M3T8M342H7")
        bounds = self.grid.get_bound()
        self.assertEqual(len(bounds), 4)

    def test_polyfill(self):
        # We need to construct a valid polygon
        from shapely.geometry import Polygon
        # A small polygon around Jakarta
        poly = Polygon([(106.8, -6.2), (106.9, -6.2), (106.9, -6.3), (106.8, -6.3)])
        cells = self.grid.polyfill(poly, 100000, start="2")
        self.assertIsInstance(cells, list)

if __name__ == '__main__':
    unittest.main()

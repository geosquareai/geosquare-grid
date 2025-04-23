import unittest
from src.geosquare_grid.core import GeosquareGrid

class TestGeosquareGrid(unittest.TestCase):

    def setUp(self):
        self.grid = GeosquareGrid()

    def test_lonlat_to_gid(self):
        gid = self.grid.lonlat_to_gid(106.894082, -6.26109, 14)
        self.assertEqual(gid, "J3N2M3T8M342")

    def test_gid_to_lonlat(self):
        lonlat = self.grid.gid_to_lonlat("J3N2M3T8M342")
        self.assertAlmostEqual(lonlat[0], 106.894082, places=5)
        self.assertAlmostEqual(lonlat[1], -6.26109, places=5)

    def test_gid_to_bound(self):
        bounds = self.grid.gid_to_bound("J3N2M3T8M342")
        self.assertEqual(bounds, (-74.0, 40.5, -73.5, 40.75))  # Example bounds

    def test_from_lonlat(self):
        self.grid.from_lonlat(106.894082, -6.26109, 14)
        self.assertEqual(self.grid.gid, "J3N2M3T8M342")

    def test_from_gid(self):
        self.grid.from_gid("J3N2M3T8M342")
        self.assertAlmostEqual(self.grid.longitude, 106.894082, places=5)
        self.assertAlmostEqual(self.grid.latitude, -6.26109, places=5)

    def test_get_gid(self):
        self.grid.from_lonlat(106.894082, -6.26109, 5)
        self.assertEqual(self.grid.get_gid(), "J3N2M3T8M342")

    def test_get_lonlat(self):
        self.grid.from_gid("J3N2M3T8M342")
        self.assertAlmostEqual(self.grid.get_lonlat()[0], 106.894082, places=5)
        self.assertAlmostEqual(self.grid.get_lonlat()[1], -6.26109, places=5)

    def test_get_bound(self):
        self.grid.from_gid("J3N2M3T8M342")
        bounds = self.grid.get_bound()
        self.assertEqual(bounds, (106.8938638928753022,-6.2613474659803572, 106.8943130505173542,-6.2608983083383016))  # Example bounds

    def test_polyfill(self):
        # Assuming polyfill method is implemented correctly
        geometry = self.grid.get_geometry()
        cells = self.grid.polyfill(geometry, 1000)
        self.assertIsInstance(cells, list)

if __name__ == '__main__':
    unittest.main()
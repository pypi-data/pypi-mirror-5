import unittest
import os

import numpy as np
	
import pyresample as pr

try:
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    pass # Postpone fail to individual tests

def tmp(f):
    f.tmp = True
    return f	

class Test(unittest.TestCase):
    
    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 
                               'test_files', 'ssmis_swath.npz'))
    data = np.load(filename)['data']
    lons = data[:, 0].astype(np.float64)
    lats = data[:, 1].astype(np.float64)
    tb37v = data[:, 2].astype(np.float64)
 
    def test_ellps2axis(self):
        a, b = pr.plot.ellps2axis('WGS84')
        self.assertAlmostEqual(a, 6378137.0, 
                                   msg='Failed to get semi-major axis of ellipsis')
        self.assertAlmostEqual(b, 6356752.3142451793, 
                                   msg='Failed to get semi-minor axis of ellipsis')
    
    def test_area_def2basemap(self):
        area_def = pr.utils.parse_area_file(os.path.join(os.path.dirname(__file__), 
                                         'test_files', 'areas.cfg'), 'ease_sh')[0]
        bmap = pr.plot.area_def2basemap(area_def)
        self.assertTrue(bmap.rmajor == bmap.rminor and 
                        bmap.rmajor == 6371228.0, 
                        'Failed to create Basemap object')

    def test_plate_carreeplot(self):
        area_def = pr.utils.parse_area_file(os.path.join(os.path.dirname(__file__), 
                                            'test_files', 'areas.cfg'), 'pc_world')[0]
        swath_def = pr.geometry.SwathDefinition(self.lons, self.lats)
        result = pr.kd_tree.resample_nearest(swath_def, self.tb37v, area_def, 
                                             radius_of_influence=20000, 
                                             fill_value=None)		
        plt = pr.plot._get_quicklook(area_def, result, num_meridians=0, 
                                     num_parallels=0)
    def test_easeplot(self):
        area_def = pr.utils.parse_area_file(os.path.join(os.path.dirname(__file__), 
                                            'test_files', 'areas.cfg'), 'ease_sh')[0]
        swath_def = pr.geometry.SwathDefinition(self.lons, self.lats)
        result = pr.kd_tree.resample_nearest(swath_def, self.tb37v, area_def, 
                                             radius_of_influence=20000, 
                                             fill_value=None)		
        plt = pr.plot._get_quicklook(area_def, result)

    def test_orthoplot(self):
        area_def = pr.utils.parse_area_file(os.path.join(os.path.dirname(__file__), 
                                            'test_files', 'areas.cfg'), 'ortho')[0]
        swath_def = pr.geometry.SwathDefinition(self.lons, self.lats)
        result = pr.kd_tree.resample_nearest(swath_def, self.tb37v, area_def, 
                                             radius_of_influence=20000, 
                                             fill_value=None)		
        plt = pr.plot._get_quicklook(area_def, result)

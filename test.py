import unittest
from mapProcessing import dailyTemp
from mapProcessing import bin


class test_DailyTemp(unittest.TestCase):
    def test_Day0(self):
        """
        Test of day zero
        """
        day = 0
        result = dailyTemp(day)
        self.assertEqual(result, 73)

    def test_Day74(self):
        """
        Test of day 74
        """
        day = 74
        result = dailyTemp(day)
        #deals with float point accuracy issues
        finalCompare = result < 81 and result > 80
        self.assertTrue(finalCompare)

class test_TempCorrect(unittest.TestCase):
    """
    Test of elevation below 1000
    """
    def test_below1000ftCorrect_dry(self):
        testBin = bin(1,1)
        testBin.elevation = 1
        testBin.temperature = 50
        testBin.tempElevationCorrection()
        self.assertEqual(testBin.temperature,50)

    """
    Test of 1000 <= elevation < 2000 and dry
    """
    def test_at1000ftCorrect_dry(self):
        testBin = bin(1,1)
        testBin.elevation = 1000
        testBin.temperature = 50
        testBin.tempElevationCorrection()
        self.assertEquals(testBin.temperature,55.4)

    """
    Test of 2000 <= elevation < 3000 and dry
    """
    def test_at2000ftCorrect_dry(self):
        testBin = bin(1,1)
        testBin.elevation = 2000
        testBin.temperature = 50
        testBin.tempElevationCorrection()
        self.assertEquals(testBin.temperature,60.8)

    """
    Test of 1000 <= elevation < 2000 and wet
    """
    def test_at1000ftCorrect_wet(self):
        testBin = bin(1,1)
        testBin.moisture = 6
        testBin.elevation = 1000
        testBin.temperature = 50
        testBin.tempElevationCorrection()
        self.assertEquals(testBin.temperature,53.3)

    """
    Test of 2000 <= elevation < 3000 and wet
    """
    def test_at2000ftCorrect_wet(self):
        testBin = bin(1,1)
        testBin.moisture = 6
        testBin.elevation = 2000
        testBin.temperature = 50
        testBin.tempElevationCorrection()
        self.assertEquals(testBin.temperature,56.6)

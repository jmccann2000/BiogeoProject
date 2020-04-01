import unittest
from mapProcessing import dailyTemp


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

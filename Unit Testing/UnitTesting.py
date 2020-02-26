from ..gedcom_parser import gedcom_parser
import unittest

class TestUserStories(unittest.TestCase):
    def test_unittest(self): #this is a test unit test
        self.assertEqual('test'.upper(), 'TEST')

if __name__ == '__main__':
    unittest.main()
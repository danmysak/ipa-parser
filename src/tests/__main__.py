from unittest import defaultTestLoader, TestSuite, TextTestRunner

from .test_api import TestApi
from .test_features import TestFeatures
from .test_known import TestKnown
from .test_loading import TestLoading

suite = TestSuite()
for test_case in [
    TestLoading,  # should be first to run properly
    TestKnown,
    TestApi,
    TestFeatures,
]:
    suite.addTest(defaultTestLoader.loadTestsFromTestCase(test_case))

TextTestRunner().run(suite)

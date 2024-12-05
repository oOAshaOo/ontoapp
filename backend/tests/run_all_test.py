import unittest
from .auth_service_tests import AuthServiceTestCase
from .users_service_tests import UserServiceTestCase
from .taxonomy_service_tests import TaxonomyServiceTestCase


def run_all_tests():
    loader = unittest.TestLoader()
    auth_tests = loader.loadTestsFromTestCase(AuthServiceTestCase)
    user_tests = loader.loadTestsFromTestCase(UserServiceTestCase)
    taxonomy_tests = loader.loadTestsFromTestCase(TaxonomyServiceTestCase)
    suite = unittest.TestSuite([auth_tests, user_tests, taxonomy_tests])
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    run_all_tests()

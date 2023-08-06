import unittest

from pystan import StanModel


class TestStanfit(unittest.TestCase):

    def test_init_zero_exception_inf_grad(self):
        code = """
        parameters {
            real x;
        }
        model {
            lp__ <- 1 / log(x);
        }
        """
        sm = StanModel(model_code=code)
        try:
            assertRaisesRegex = self.assertRaisesRegex
        except AttributeError:
            assertRaisesRegex = self.assertRaisesRegexp
        with assertRaisesRegex(RuntimeError, 'divergent gradient'):
            sm.sampling(init='0', iter=1)

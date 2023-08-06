import logging
import os
import tempfile
import time
import unittest

import numpy as np

from pystan import StanModel


class TestBernoulli(unittest.TestCase):

    bernoulli_model_code = """
        data {
        int<lower=0> N;
        int<lower=0,upper=1> y[N];
        }
        parameters {
        real<lower=0,upper=1> theta;
        }
        model {
        for (n in 1:N)
            y[n] ~ bernoulli(theta);
        }
        """
    bernoulli_data = {'N': 10, 'y': [0, 1, 0, 0, 0, 0, 0, 0, 0, 1]}

    model = StanModel(model_code=bernoulli_model_code, model_name="bernoulli")

    def test_simple_model_constructor(self):
        m = StanModel(model_code='parameters {real y;} model {y ~ normal(0,1);}',
                    model_name="normal1", verbose=True)
        self.assertEqual(m.model_name, "normal1")

    def test_bernoulli_constructor(self):
        model = self.model
        self.assertEqual(model.model_name, "bernoulli")
        self.assertTrue(model.model_cppname.endswith("bernoulli"))

    def test_bernoulli_compile_time(self):
        model_code = self.bernoulli_model_code
        t0 = time.time()
        model = StanModel(model_code=model_code)
        self.assertIsNotNone(model)
        msg = "Compile time: {}s (vs. RStan 28s)\n".format(int(time.time()-t0))
        logging.info(msg)

    def test_bernoulli_sampling(self):
        fit = self.model.sampling(data=self.bernoulli_data)
        self.assertEqual(fit.sim['iter'], 2000)
        self.assertEqual(fit.sim['pars_oi'], ['theta', 'lp__'])
        self.assertEqual(len(fit.sim['samples']), 4)
        assert 0.1 < np.mean(fit.sim['samples'][0]['chains']['theta']) < 0.4
        assert 0.1 < np.mean(fit.sim['samples'][1]['chains']['theta']) < 0.4
        assert 0.1 < np.mean(fit.sim['samples'][2]['chains']['theta']) < 0.4
        assert 0.1 < np.mean(fit.sim['samples'][3]['chains']['theta']) < 0.4
        assert 0.01 < np.var(fit.sim['samples'][0]['chains']['theta']) < 0.02
        assert 0.01 < np.var(fit.sim['samples'][1]['chains']['theta']) < 0.02
        assert 0.01 < np.var(fit.sim['samples'][2]['chains']['theta']) < 0.02
        assert 0.01 < np.var(fit.sim['samples'][3]['chains']['theta']) < 0.02

    def test_bernoulli_sampling_error(self):
        bad_data = self.bernoulli_data.copy()
        del bad_data['N']
        try:
            assertRaisesRegex = self.assertRaisesRegex
        except AttributeError:
            assertRaisesRegex = self.assertRaisesRegexp
        with assertRaisesRegex(RuntimeError, 'variable does not exist'):
            fit = self.model.sampling(data=bad_data)

    def test_bernoulli_extract(self):
        fit = self.model.sampling(data=self.bernoulli_data)
        extr = fit.extract(permuted=True)
        assert -7.4 < np.mean(extr['lp__']) < -7.0
        assert 0.1 < np.mean(extr['theta']) < 0.4
        assert 0.01 < np.var(extr['theta']) < 0.02

        # permuted=False
        extr = fit.extract(permuted=False)
        self.assertEqual(extr.shape, (1000, 4, 2))
        self.assertTrue(0.1 < np.mean(extr[:, 0, 0]) < 0.4)

        # permuted=True
        extr = fit.extract('lp__', permuted=True)
        assert -7.4 < np.mean(extr['lp__']) < -7.0
        extr = fit.extract('theta', permuted=True)
        assert 0.1 < np.mean(extr['theta']) < 0.4
        assert 0.01 < np.var(extr['theta']) < 0.02
        extr = fit.extract('theta', permuted=False)
        assert extr.shape == (1000, 4, 2)
        assert 0.1 < np.mean(extr[:, 0, 0]) < 0.4

    def test_bernoulli_summary(self):
        fit = self.model.sampling(data=self.bernoulli_data)
        s = fit.summary()
        repr(fit)
        print(fit)

    def test_bernoulli_sample_file(self):
        tmpdir = tempfile.mkdtemp()
        sample_file = os.path.join(tmpdir, 'sampling.csv')
        sample_file_base = os.path.splitext(os.path.basename(sample_file))[0]
        fit = self.model.sampling(data=self.bernoulli_data, sample_file=sample_file)
        assert all([sample_file_base in fn for fn in os.listdir(tmpdir)])

        fit = self.model.sampling(data=self.bernoulli_data, sample_file='/tmp/doesnotexist')
        assert fit is not None

        tmpdir = tempfile.mkdtemp()
        sample_file = 'opt.csv'
        sample_file_base = os.path.splitext(os.path.basename(sample_file))[0]
        fit = self.model.optimizing(data=self.bernoulli_data, sample_file=sample_file)
        # not working right now -- it's a stan issue, not a pystan issue.

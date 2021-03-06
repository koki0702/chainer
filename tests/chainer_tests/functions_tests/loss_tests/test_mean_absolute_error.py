import unittest

import numpy

import chainer
from chainer import cuda
from chainer import functions
from chainer import gradient_check
from chainer import testing
from chainer.testing import attr


class TestMeanAbsoluteError(unittest.TestCase):

    def setUp(self):
        self.x0 = numpy.random.uniform(-1, 1, (4, 3)).astype(numpy.float32)
        # Add sufficient margin to prevent computational error
        diff = numpy.random.uniform(-1, 1, (4, 3)).astype(numpy.float32)
        diff[abs(diff) < 0.01] = 0.5
        self.x1 = self.x0 + diff
        self.gy = numpy.random.uniform(-1, 1, ()).astype(numpy.float32)
        self.ggx0 = numpy.random.uniform(-1, 1, (4, 3)).astype(numpy.float32)
        self.ggx1 = numpy.random.uniform(-1, 1, (4, 3)).astype(numpy.float32)

    def check_forward(self, x0_data, x1_data):
        x0 = chainer.Variable(x0_data)
        x1 = chainer.Variable(x1_data)
        loss = functions.mean_absolute_error(x0, x1)
        loss_value = cuda.to_cpu(loss.data)

        assert loss_value.dtype == numpy.float32
        assert loss_value.shape == ()

        # Compute expected value
        loss_expect = 0.
        for i in numpy.ndindex(self.x0.shape):
            loss_expect += abs(self.x0[i] - self.x1[i])
        loss_expect /= self.x0.size

        assert round(loss_expect - loss_value, 5) == 0

    def test_forward_cpu(self):
        self.check_forward(self.x0, self.x1)

    @attr.gpu
    def test_forward_gpu(self):
        self.check_forward(cuda.to_gpu(self.x0), cuda.to_gpu(self.x1))

    def check_backward(self, x0_data, x1_data):
        gradient_check.check_backward(
            functions.mean_absolute_error, (x0_data, x1_data), None, eps=1e-2)

    def test_backward_cpu(self):
        self.check_backward(self.x0, self.x1)

    @attr.gpu
    def test_backward_gpu(self):
        self.check_backward(cuda.to_gpu(self.x0), cuda.to_gpu(self.x1))

    def check_double_backward(self, x0_data, x1_data, gy_data, ggx0_data,
                              ggx1_data):
        def f(*xs):
            y = chainer.functions.mean_absolute_error(*xs)
            return y * y

        gradient_check.check_double_backward(
            f, (x0_data, x1_data), gy_data, (ggx0_data, ggx1_data), eps=1e-2)

    def test_double_backward_cpu(self):
        self.check_double_backward(
            self.x0, self.x1, self.gy, self.ggx0, self.ggx1)

    @attr.gpu
    def test_double_backward_gpu(self):
        self.check_double_backward(cuda.to_gpu(self.x0),
                                   cuda.to_gpu(self.x1),
                                   cuda.to_gpu(self.gy),
                                   cuda.to_gpu(self.ggx0),
                                   cuda.to_gpu(self.ggx1))


testing.run_module(__name__, __file__)

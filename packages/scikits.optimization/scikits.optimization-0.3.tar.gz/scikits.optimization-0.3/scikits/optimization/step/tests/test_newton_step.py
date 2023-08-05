#/usr/bin/env python

import unittest
import numpy
from numpy.testing import *
from .. import NewtonStep

class Function(object):
  def __call__(self, x):
    return (x[0] - 2.) ** 2 + (2 * x[1] + 4) ** 2

  def gradient(self, x):
    return numpy.array((2. * (x[0] - 2), 4 * (2 * x[1] + 4)))

  def hessian(self, x):
    return numpy.diag((2., 8.))

class test_NewtonStep(unittest.TestCase):
  def test_call(self):
    step = NewtonStep()
    state = {}
    function = Function()
    assert_equal(step(function = function, point = numpy.zeros((2)), state = state), numpy.array((2., -2.)))

if __name__ == "__main__":
  unittest.main()
import parakeet 
from parakeet import jit 
import numpy as np
import testing_helpers
 

@jit
def avg1d(x):
  return sum(x) / float(len(x))

def test_avg1d():
  x = np.random.randn(20)
  testing_helpers.eq(x.mean(), avg1d(x))

@jit
def winmap_avg1d(x, w = 3):
  return parakeet.pmap1d(avg1d, x, w)

def test_winmap_avg1d():
  x = np.random.randn(20)**2
  y = winmap_avg1d(x)
  assert x.shape == y.shape

 
@jit
def avg2d(x):
  nelts = x.shape[0] * x.shape[1]
  return sum(sum(x)) / float(nelts)

def test_avg2d():
  x = np.random.randn(20,30)
  testing_helpers.eq(x.mean(), avg2d(x))

@jit
def winmap_zeros(x, wx = 3, wy = 3):
  def zero(_):
    return 0
  return parakeet.pmap2d(zero, x, (wx, wy))

def test_winmap_zeros():
  x = np.random.randn(100,100)
  y = winmap_zeros(x)
  assert y.sum() == 0

@jit
def winmap_first_elt(x, wx = 3, wy = 3):
  def f(window):
    return window[0,0]
  return parakeet.pmap2d(f, x, wx, wy)

"""
def test_winmap_first_elt():
  x = np.random.randn(10,5)**2
  y = winmap_first_elt(x)
  assert (y > 0).all()
"""

def test_window_shapes():
  x = np.array([0,1,2,3,4])
  def winshape(x):
    return x.shape[0] 
  y = parakeet.pmap1d(winshape, x, 3)
  expected = np.array([2,3,3,3,2])
  assert y.shape == expected.shape and np.all(y == expected)

@jit
def winavg2d( x, wx = 3, wy = 3):
  return parakeet.pmap2d(avg2d, x, (wx, wy))

def test_winavg2d():
  x = np.random.rand(100,100)
  x[50:65, 50:65] = 0
  y = winavg2d(x)
  assert x.shape==y.shape
  assert x.max() >= y.max()
  assert x.min() <= y.min()
  
  
if __name__ == '__main__':
  testing_helpers.run_local_tests()
  

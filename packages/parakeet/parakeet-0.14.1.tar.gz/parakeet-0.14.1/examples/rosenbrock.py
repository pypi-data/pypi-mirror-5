
# Rosenbrock function derivative
# 
# Copied from https://github.com/numfocus/python-benchmarks/blob/master/rosen_der/rosen_der_python.py
# Original authors: Travis Oliphant (NumPy version) & Serge Guelton (loops version)
#

import numpy as np 
from parakeet import jit 

def rosen_der_np(x):
  xm = x[1:-1]
  xm_m1 = x[:-2]
  xm_p1 = x[2:]
  der = np.empty_like(x)
  der[1:-1] = (+ 200 * (xm - xm_m1 ** 2)
               - 400 * (xm_p1 - xm ** 2) * xm
               - 2 * (1 - xm))
  der[0] = -400 * x[0] * (x[1] - x[0] ** 2) - 2 * (1 - x[0])
  der[-1] = 200 * (x[-1] - x[-2] ** 2)
  return der

def rosen_der_loops(x):
  n = x.shape[0]
  der = np.empty_like(x)

  for i in range(1, n - 1):
    der[i] = (+ 200 * (x[i] - x[i - 1] ** 2)
              - 400 * (x[i + 1]
              - x[i] ** 2) * x[i]
              - 2 * (1 - x[i]))
  der[0] = -400 * x[0] * (x[1] - x[0] ** 2) - 2 * (1 - x[0])
  der[-1] = 200 * (x[-1] - x[-2] ** 2)
  return der

if __name__ == '__main__':
  N = 10**5
  x = np.arange(N) / float(N)
  jit(rosen_der_np)(x) 
  from timer import compare_perf
  compare_perf(rosen_der_np, [x.copy()], numba=False)
  compare_perf(rosen_der_loops, [x.copy()], numba=False)

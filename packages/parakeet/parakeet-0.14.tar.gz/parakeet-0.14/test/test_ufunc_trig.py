import numpy as np 

from testing_helpers import run_local_tests, expect  


int_array = np.array([0,1])
bool_array = np.array([False,True])
float_array = np.array([0.1, 0.2])
arrays = [int_array, bool_array, float_array]

def unary(fn): 
  for x in arrays:
    expect(fn, [x], fn(x))

def binary(fn):
  for x in arrays:
      for y in arrays:
          expect(fn, [x,y], fn(x,y))

def test_sin():
  unary(np.sin)

def test_cos():
  unary(np.cos)
  
def test_tan():
  unary(np.tan)
  
def test_arcsin():
  unary(np.arcsin)
  
def test_arccos():
  unary(np.arccos)
  
def test_arctan():
  unary(np.arctan)
  
def test_arctan2():
  binary(np.arctan2)
  
  
def test_sinh():
  unary(np.sinh)
  
def test_cosh():
  unary(np.cosh)
  
def test_tanh():
  unary(np.tanh)
  
def test_arcsinh():
  unary(np.arcsinh)
  
def test_arccosh():
  unary(np.arccosh)
  
def test_arctanh():
  unary(np.arctanh)
  
def test_deg2rad():
  unary(np.deg2rad)
  
def test_rad2deg():
  unary(np.rad2deg)
  
#def test_hypot():
#  binary(np.hypot)

if __name__ == '__main__':
  run_local_tests() 

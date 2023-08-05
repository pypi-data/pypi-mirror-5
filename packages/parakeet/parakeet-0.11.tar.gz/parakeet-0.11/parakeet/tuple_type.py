import ctypes

import type_conv

from core_types import IncompatibleTypes, StructT
from syntax import Expr, Const

class TupleT(StructT):
  rank = 0
  _members = ['elt_types']

  # signals to type inference algorithm to pass the value of an index into
  # index_type rather than its type
  static_indexing = True

  def node_init(self):
    if self.elt_types is None:
      self.elt_types = ()
    self.elt_types = tuple(self.elt_types)
    self._fields_ = [("elt%d" % i, t) for (i,t) in enumerate(self.elt_types)]

  def from_python(self, python_tuple, _keep_forever = []):
    # _keep_forever.append(python_tuple)
    converted_elts = []
    for elt in python_tuple:
      parakeet_type = type_conv.typeof(elt)
      c_elt = parakeet_type.from_python(elt)

      if isinstance(parakeet_type, StructT):
        c_elt = ctypes.pointer(c_elt)
      converted_elts.append(c_elt)
    return self.ctypes_repr(*converted_elts)

  def to_python(self, struct_obj):
    elt_values = []
    for (field_name, field_type) in self._fields_:
      c_elt = getattr(struct_obj, field_name)
      if isinstance(field_type, StructT):
        c_elt = c_elt.contents

      py_elt = field_type.to_python(c_elt)

      elt_values.append(py_elt)
    return tuple(elt_values)

  def dtype(self):
    raise RuntimeError("Do tuples have dtypes?")

  def __eq__(self, other):
    return isinstance(other, TupleT) and self.elt_types == other.elt_types

  def __hash__(self):
    return hash(self.elt_types)

  def __str__(self):
    return "tuple(%s)" % ", ".join([str(t) for t in self.elt_types])

  def __repr__(self):
    return str(self)

  def __len__(self):
    return len(self.elt_types)

  def __iter__(self):
    return iter(self.elt_types)

  def index_type(self, idx):
    assert isinstance(idx, Expr), \
        "Tuple index not an expression: %s" % idx
    assert isinstance(idx, Const), "Unsupported expression: %s" % idx
    idx = int(idx.value)
    assert 0 <= idx < len(self.elt_types), \
        "Can't get element %d from tuple of length %d" % \
        (idx, len(self.elt_types))
    return self.elt_types[idx]

  def combine(self, other):
    if isinstance(other, TupleT) and \
       len(other.elt_types) == len(self.elt_types):
      combined_elt_types = [t1.combine(t2) for
                            (t1, t2) in zip(self.elt_types, other.elt_types)]
      if combined_elt_types != self.elt_types:
        return TupleT(combined_elt_types)
      else:
        return self
    else:
      raise IncompatibleTypes(self, other)

_tuple_types = {}
def repeat_tuple(t, n):
  """Given the base type t, construct the n-tuple t*t*...*t"""

  elt_types = tuple([t] * n)
  if elt_types in _tuple_types:
    return _tuple_types[elt_types]
  else:
    tuple_t = TupleT(elt_types)
    _tuple_types[elt_types] = tuple_t
    return tuple_t

def make_tuple_type(elt_types):
  """
  Use this memoized construct to avoid constructing too many distinct tuple type
  objects and speeding up equality checks
  """

  key = tuple(elt_types)
  if key in _tuple_types:
    return _tuple_types[key]
  else:
    t = TupleT(key)
    _tuple_types[key] = t
    return t



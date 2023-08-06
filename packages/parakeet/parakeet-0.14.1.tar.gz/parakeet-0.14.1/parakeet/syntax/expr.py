from treelike import Node 

from .. ndtypes import NoneT, make_tuple_type

class Expr(Node):
  _members = ['type']
  
  def children(self):
    for v in self.itervalues():
      if v and isinstance(v, Expr):
        yield v
      elif isinstance(v, (list,tuple)):
        for child in v:
          if isinstance(child, Expr):
            yield child

  def short_str(self):
    return str(self)

class Const(Expr):
  _members = ['value']
  
  def children(self):
    return ()

  def short_str(self):
    return str(self.value)

  def __repr__(self):
    if self.type and not isinstance(self.type, NoneT):
      return "%s : %s" % (self.value, self.type)
    else:
      return str(self.value)

  def __str__(self):
    return repr(self)

  def __hash__(self):
    return hash(self.value)

  def __eq__(self, other):
    return other.__class__ is Const and \
           self.value == other.value and \
           self.type == other.type
    
  def __ne__(self, other):
    return other.__class__ is not Const or \
           self.value != other.value or \
           self.type != other.type

class Var(Expr):
  _members = ['name']

  def node_init(self):
    assert self.name is not None
    
  def short_str(self):
    return self.name

  def __repr__(self):
    if hasattr(self, 'type'):
      return "%s : %s" % (self.name, self.type)
    else:
      return "%s" % self.name

  def __str__(self):
    return self.name

  def __hash__(self):
    return hash(self.name)

  def __eq__(self, other):
    return other.__class__  is Var and \
           self.name == other.name and \
           self.type == other.type


  def __ne__(self, other):
    return other.__class__ is not Var or \
           self.name != other.name or \
           self.type != other.type
  
  def children(self):
    return ()

class Attribute(Expr):
  _members = ['value', 'name']

  def children(self):
    yield self.value

  def __str__(self):
    return "attr(%s, '%s')" % (self.value, self.name)

  def __hash__(self):
    return hash ((self.value, self.name))

  def __eq__(self, other):
    return other.__class__ is Attribute and \
           self.name == other.name and \
           self.value == other.value


class Tuple(Expr):
  _members = ['elts']

  def node_init(self):
    self.elts = tuple(self.elts)
    if self.type is None and all(e.type is not None for e in self.elts):
      self.type = make_tuple_type(tuple(e.type for e in self.elts))
      
  def __str__(self):
    if len(self.elts) > 0:
      return ", ".join([str(e) for e in self.elts])
    else:
      return "()"
    
  def children(self):
    return self.elts

  def __hash__(self):
    return hash(self.elts)


class Closure(Expr):
  """Create a closure which points to a global fn with a list of partial args"""

  _members = ['fn', 'args']

  def __str__(self):
    fn_str = str(self.fn) #self.fn.name if hasattr(self.fn, 'name') else str(self.fn)
    args_str = ",".join(str(arg) + ":" + str(arg.type) for arg in self.args)
    return "Closure(%s, fixed_args = {%s})" % (fn_str, args_str)

  def node_init(self):
    self.args = tuple(self.args)

  def children(self):
    if isinstance(self.fn, Expr):
      yield self.fn
    for arg in self.args:
      yield arg

  def __hash__(self):
    return hash((self.fn, tuple(self.args)))

class Call(Expr):
  _members = ['fn', 'args']

  def __str__(self):
    #if isinstance(self.fn, (Fn, TypedFn)):
    #  fn_name = self.fn.name
    #else:
    fn_name = str(self.fn)
    if self.args.__class__.__name__ == 'ActualArgs':
      arg_str = str(self.args)
    else:
      arg_str = ", ".join(str(arg) for arg in self.args)
    return "%s(%s)" % (fn_name, arg_str)

  def __repr__(self):
    return str(self)

  def children(self):
    yield self.fn
    for arg in self.args:
      yield arg

  def __hash__(self):
    return hash((self.fn, tuple(self.args)))


class PrimCall(Expr):
  """
  Call a primitive function, the "prim" field should be a prims.Prim object
  """
  _members = ['prim', 'args']
  
  def _arg_str(self, i):
    arg = self.args[i]
    if arg.__class__ is PrimCall:
      return "(%s)" % arg
    else:
      return str(arg)
  
  def __hash__(self):
    self.args = tuple(self.args)
    return hash((self.prim, self.args))
    
  def __eq__(self, other):
    if other.__class__ is not PrimCall:
      return False 
    
    if other.prim != self.prim:
      return False
    
    my_args = self.args
    other_args = other.args
    n = len(my_args)
    if n != len(other_args):
      return False
    
    for (i,arg) in enumerate(my_args):
      other_arg = other_args[i]
      if arg != other_arg:
        return False
    return True
  
  def __ne__(self, other):
    return not self==other
  
  def __repr__(self):
    if self.prim.symbol:
      if len(self.args) == 1:
        return "%s%s" % (self.prim.symbol, self._arg_str(0))
      else:
        assert len(self.args) == 2
        return "%s %s %s" % (self._arg_str(0), self.prim.symbol, self._arg_str(1))
    else:
      arg_strings = [self._arg_str(i) for i in xrange(len(self.args))]
      combined = ", ".join(arg_strings)
      return "prim<%s>(%s)" % (self.prim.name, combined)

  def __str__(self):
    return repr(self)

  def node_init(self):
    self.args = tuple(self.args)

  def children(self):
    return self.args
  


class TupleProj(Expr):
  _members = ['tuple', 'index']

  def node_init(self):
    if self.type is None:
      if self.tuple.type is not None and self.index.__class__ is Const:
        self.type = self.tuple.type.elt_types[self.index.value]
            
  def __str__(self):
    return "TupleProj(%s, %d)" % (self.tuple, self.index)

  def children(self):
    return (self.tuple,)

  def __hash__(self):
    return hash((self.tuple, self.index))

class ClosureElt(Expr):
  _members = ['closure', 'index']

  def __str__(self):
    return "ClosureElt(%s, %d)" % (self.closure, self.index)

  def children(self):
    return (self.closure,)

  def __hash__(self):
    return hash((self.closure, self.index))

class Cast(Expr):
  # inherits the member 'type' from Expr, but for Cast nodes it is mandatory
  _members = ['value']

  def __hash__(self):
    return hash(self.value)
  
  def __str__(self):
    return "Cast(%s : %s)" % (self.value, self.type) 

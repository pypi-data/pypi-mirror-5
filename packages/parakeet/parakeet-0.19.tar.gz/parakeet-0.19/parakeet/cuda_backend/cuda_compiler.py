import numpy as np 
import pycuda 

from .. import names
from ..builder import build_fn
# from ..c_backend import FnCompiler
from ..ndtypes import TupleT,  Int32, FnT, ScalarT, SliceT, NoneT, ArrayT, ClosureT
from ..c_backend import PyModuleCompiler
from ..openmp_backend import MulticoreCompiler
from ..syntax import PrintString, SourceExpr
from ..syntax.helpers import get_types, get_fn, get_closure_args, const_int, zero_i32, one_i32

import config 
import device_info 
from cuda_syntax import threadIdx, blockIdx, blockDim 


class CudaCompiler(MulticoreCompiler):
  
  def __init__(self, *args, **kwargs):
    # keep track of which kernels we've already compiled 
    # and map the name of the nested function to its kernel name
    self._kernel_cache = {}
    if 'gpu_depth' in kwargs:
      self.gpu_depth = kwargs['gpu_depth'] 
      del kwargs['gpu_depth']
    else:
      self.gpu_depth = 0
    
    self.device = device_info.best_cuda_device()
    assert self.device, "No GPU found"
    
    self.use_constant_memory_for_args = True
    MulticoreCompiler.__init__(self, 
                               compiler_cmd = ['nvcc', '-arch=sm_13'], 
                               extra_link_flags = ['-lcudart'], 
                               src_extension = '.cu',  
                               compiler_flag_prefix = '-Xcompiler',
                               linker_flag_prefix = '-Xlinker', 
                               *args, **kwargs)
  
  @property 
  def cache_key(self):
    return self.__class__, self.depth > 0, max(self.gpu_depth, 2) 
  
  def enter_module_body(self):
    self.append('cudaSetDevice(%d);' % device_info.device_id(self.device))
  
  
  def build_kernel(self, clos, bounds):
    n_indices = len(bounds)
    fn = get_fn(clos)
    outer_closure_exprs = get_closure_args(clos)
    closure_arg_types = get_types(outer_closure_exprs)
    host_closure_args = self.visit_expr_list(outer_closure_exprs)
    
    self.comment("Copying data from closure arguments to the GPU")
    gpu_closure_args = \
      [self.to_gpu(c_expr, t) for (c_expr, t) in 
       zip(host_closure_args, closure_arg_types)]
    
    input_types = fn.input_types 
    
    #nested_fn_name, outer_closure_args, input_types = \
    # self.get_fn_info(fn, attributes = ["__device__"])
    #key = fn.cache_key, self.cache_key
    #if key in self._kernel_cache:
    #  kernel_name = self._kernel_cache[key]
    #  return kernel_name, None #gpu_closure_args, host_closure_args, closure_arg_types
    
    kernel_name = names.fresh("kernel_" + fn.name)
    
    if isinstance(input_types[-1], TupleT):
      index_types = input_types[-1].elt_types   
      index_as_tuple = True
      # if function takes a tuple of 
      closure_arg_types = input_types[:-1]
    else:
      index_types = input_types[-n_indices:]
      index_as_tuple = False
      closure_arg_types = input_types[:-n_indices]
      
    n_closure_args = len(closure_arg_types)
    assert len(outer_closure_exprs) == n_closure_args, \
      "Mismatch between closure formal args %s and given %s" % (", ".join(closure_arg_types),
                                                                ", ".join(outer_closure_exprs))
    bound_types = (Int32,) * n_indices
    
    if self.use_constant_memory_for_args:
      outer_input_types = tuple(bound_types)
    else:
      outer_input_types = tuple(closure_arg_types) + bound_types
      
    
        
    
    parakeet_kernel, builder, input_vars  = build_fn(outer_input_types, name = kernel_name)
    
    if self.use_constant_memory_for_args:
      inner_closure_vars = []
      for i, t in enumerate(closure_arg_types):
        raw_name = fn.arg_names[i]
        self.comment("Moving GPU arg #%d %s : %s to constant memory" % (i, raw_name, t))
        const_name = self.fresh_name("gpu_arg_"  + raw_name)
        typename = self.to_ctype(t)
        self.add_decl("__constant__ %s %s" % (typename, const_name))
        inner_closure_vars.append(SourceExpr(const_name, type=t))
        gpu_arg = gpu_closure_args[i]
        # in case this is a constant, should assign to a variable
        first_char = gpu_arg[0]
        if not first_char.isalpha():
          gpu_arg = self.fresh_var(typename, "src_" + raw_name, gpu_arg)
        self.append("cudaMemcpyToSymbolAsync(%s, &%s, sizeof(%s));" % (const_name, gpu_arg, typename))
      inner_closure_vars = tuple(inner_closure_vars)
      # need to do a cudaMemcpyToSymbol for each gpu arg   
      bounds_vars = input_vars
  
    else:
      # TODO: use these to compute indices when n_indices > 3 or 
      # number of threads per block > 1  
      inner_closure_vars = input_vars[:n_closure_args]
      bounds_vars = input_vars[n_closure_args:(n_closure_args + n_indices)]


    """
       upper_bounds, 
       loop_body, 
       lower_bounds = None, 
       step_sizes = None
    """
    
    
    BLOCKS_PER_SM = config.blocks_per_sm 
    THREADS_PER_DIM = config.threads_per_block_dim 

    start_idx = builder.add(builder.mul(blockDim.x, blockIdx.x, "base_x"), 
                            threadIdx.x,  name = "start_x")
    start_indices = [start_idx]
    
    stop_x = builder.mul(builder.add(one_i32, blockIdx.x, "next_base_x"), 
                         blockDim.x, "stop_x")
    stop_x = builder.min(stop_x, bounds_vars[0], "stop_x") 
    stop_indices = [stop_x]
    if n_indices == 1:
      step_sizes = [const_int(THREADS_PER_DIM**2, Int32)]
       
    if n_indices > 1:

      start_idx_y = builder.add(builder.mul(blockDim.y, blockIdx.y, "base_y"),
                                threadIdx.y, "start_y")
      start_indices.append(start_idx_y)
      
      stop_y = builder.mul(builder.add(one_i32, blockIdx.y, "next_base_y"),
                           blockDim.y, "stop_y") 
      stop_y = builder.min(stop_y, bounds_vars[1], "stop_y") 
      stop_indices.append(stop_y)
      
      step_sizes = [const_int(THREADS_PER_DIM, Int32), const_int(THREADS_PER_DIM, Int32)]
      for i in xrange(2, n_indices):
        start_indices.append(zero_i32)
        step_sizes.append(one_i32)
        stop_indices.append(bounds_vars[i])
        
    def loop_body(index_vars):
      if not isinstance(index_vars, (list,tuple)):
        pass
      indices = [builder.cast(idx, t) for idx, t in zip(index_vars,index_types)]
      if index_as_tuple:
        index_args = (builder.tuple(indices),)
      else:
        index_args = indices
      inner_args = tuple(inner_closure_vars) + tuple(index_args)
      builder.call(fn, inner_args)
      
    builder.nested_loops(stop_indices, loop_body, start_indices, step_sizes, index_vars_as_list = True)
    
    self.enter_kernel()
    c_kernel_name = self.get_fn_name(parakeet_kernel, 
                                     attributes = ["__global__"], 
                                     inline = False)
    self.exit_kernel()
    
    # self._kernel_cache[key] = c_kernel_name
    return c_kernel_name, gpu_closure_args, host_closure_args, closure_arg_types
  
  def launch_kernel(self, bounds, params, kernel_name):
    self.synchronize("Done copying arguments to GPU, prepare for kernel launch")
    
    n_bounds = len(bounds)
    sm_count = device_info.num_multiprocessors(self.device)
    n_blocks = sm_count * config.blocks_per_sm 
    
    THREADS_PER_DIM = config.threads_per_block_dim
    
    if n_bounds == 1:
      grid_dims = [n_blocks, 1, 1]
      block_dims = [THREADS_PER_DIM**2, 1, 1]
    else:
      blocks_per_axis = int(np.ceil(np.sqrt(n_blocks)))
      grid_dims = [blocks_per_axis, blocks_per_axis, 1]
      block_dims = [THREADS_PER_DIM,THREADS_PER_DIM,1]

    grid_dims_str = "dim3(%s)" % ", ".join( str(d) for d in grid_dims)
    block_dims_str = "dim3(%s)" % ", ".join( str(d) for d in block_dims)
    
    self.comment("kernel launch")
    
    kernel_args_str = ", ".join(params)
    self.append("%s<<<%s, %s>>>(%s);" % (kernel_name, grid_dims_str, block_dims_str, kernel_args_str))
  
    self.comment("After launching kernel, synchronize to make sure the computation is done")
    self.synchronize("Finished kernel launch")
    
    
  
  def visit_ParFor(self, stmt):
    bounds = self.tuple_to_var_list(stmt.bounds)

    n_indices = len(bounds)
    if n_indices > 5 or not self.in_host():
      return MulticoreCompiler.visit_ParFor(self, stmt)

    
    kernel_name, gpu_closure_args, host_closure_args, closure_arg_types  = \
      self.build_kernel(stmt.fn, bounds)
    
    if self.use_constant_memory_for_args:
      params = bounds 
    else:
      params = tuple(gpu_closure_args) + tuple(bounds)
      
    self.launch_kernel(bounds, params, kernel_name)
    
    self.comment("copy arguments back from the GPU to the host")
    self.list_to_host(host_closure_args, gpu_closure_args, closure_arg_types)
    return "/* done with ParFor */"
  
  """
  def visit_NumCores(self, expr):
    # by default we're running sequentially 
    sm_count = None # TODO
    active_thread_blocks = 6 
    return "%d" % (sm_count * active_thread_blocks)  
  """
  
  def in_host(self):
    return self.gpu_depth == 0
  
  def in_block(self):
    return self.gpu_depth == 1
  
  def in_gpu(self):
    return self.gpu_depth > 0
  
  def get_fn_name(self, fn_expr, attributes = [], inline = True):
    if self.in_gpu() and not attributes:
      attributes = ["__device__"] 
    kwargs = {'depth':self.depth, 'gpu_depth':self.gpu_depth}
    return PyModuleCompiler.get_fn_name(self, fn_expr, 
                                        compiler_kwargs = kwargs,
                                        attributes = attributes, 
                                        inline = inline)
    

  
  def enter_kernel(self):
    """
    Keep a stack of adverb contexts so we know when we're global vs. block vs. thread
    """
    self.depth += 1
    self.gpu_depth += 1  
  
  def exit_kernel(self):
    self.depth -= 1
    self.gpu_depth -= 1 
  
  
  def in_thread(self):
    return self.depth > 1
  
  
  
  
  def pass_by_value(self, t):
    if isinstance(t, (ScalarT, NoneT, SliceT, FnT)):
      return True 
    elif isinstance(t, TupleT):
      return all(self.pass_by_value(elt_t) for elt_t in t.elt_types)
    elif isinstance(t, ClosureT):
      return all(self.pass_by_value(elt_t) for elt_t in t.arg_types)
    return False 
  
  
  def check_gpu_error(self, context = None, error_code_var = None):
    if error_code_var is None:
      error_code_var = self.fresh_name("cuda_err")
      self.append("cudaError %s = cudaGetLastError();" % error_code_var)
    if context is None:
      context = "\"Generated CUDA source at \" __FILE__ \" : \" __LINE__"
    self.append("""
      if ( cudaSuccess != %s ) {
        printf( "Error after %s: %%s\\n",  cudaGetErrorString(%s) );
      }
    """ % (error_code_var, context, error_code_var))
  
  def synchronize(self, context = None):
    error_code_var = self.fresh_name("cuda_err")
    self.append("cudaError %s = cudaDeviceSynchronize();" % error_code_var)
    self.check_gpu_error(context, error_code_var)
    
  
  def to_gpu(self, c_expr, t):
    if self.pass_by_value(t):
      return c_expr
    elif isinstance(t, ArrayT):
      ptr_t = "%s*" % self.to_ctype(t.elt_type)
      bytes_per_elt = t.elt_type.dtype.itemsize
      src = "%s.data.raw_ptr" % c_expr  
      dst = self.fresh_var(ptr_t, "gpu_ptr")
      nelts = "%s.size" % c_expr
      nbytes = self.fresh_var("int64_t", "nbytes", "%s * %d" % (nelts, bytes_per_elt))
      # allocate the destination pointer on the GPU
      
      self.append("cudaMalloc( (void**) &%s, %s);" % (dst, nbytes))
      self.check_gpu_error("cudaMalloc for %s : %s" % (c_expr, t))
      
      # copy the contents of the host array to the GPU
      self.append("cudaMemcpyAsync(%s, %s, %s, cudaMemcpyHostToDevice);" % (dst, src, nbytes))
      
      # self.check_gpu_error("Memcpy of %s : %s (%s -> %s)" % (c_expr, t, src, dst))
      # make an identical array descriptor but change its data pointer to the GPU location
      gpu_descriptor = self.fresh_var(self.to_ctype(t), "gpu_array", c_expr)
      self.append("%s.data.raw_ptr = %s;" % (gpu_descriptor, dst))
      return gpu_descriptor
    
    elif isinstance(t, (ClosureT, TupleT)):
      # copy contents of the host tuple into another struct
      gpu_tuple = self.fresh_var(self.to_ctype(t), "gpu_tuple", c_expr)
      for i, elt_t in enumerate(t.elt_types):
        gpu_elt = self.to_gpu("%s.elt%d" % (c_expr, i), elt_t)
        self.append("%s.elt%d = %s;" % (c_expr, i, gpu_elt))
      return gpu_tuple 
    else:
      assert False, "Unsupported type in CUDA backend %s" % t 
  
  def list_to_gpu(self, host_values, types):
    return [self.to_gpu(v,t) for (v,t) in zip(host_values, types)]
  
  
  def to_host(self, host_value, gpu_value, t):
    if self.pass_by_value(t):
      return
    elif isinstance(t, ArrayT):
      dst = "%s.data.raw_ptr" % host_value 
      src = "%s.data.raw_ptr"  % gpu_value 
      nelts = "%s.size" % gpu_value
      nbytes = "%s * %d" % (nelts, t.elt_type.dtype.itemsize)  
      self.append("cudaMemcpy(%s, %s, %s, cudaMemcpyDeviceToHost);" % (dst, src, nbytes) )
      self.append("cudaFree(%s);" % src) 

    elif isinstance(t, (ClosureT, TupleT)):
      for i, elt_t in enumerate(t.elt_types):
        host_elt = "%s.elt%d" % (host_value, i)
        gpu_elt = "%s.elt%d" % (gpu_value, i)
        self.to_host(host_elt, gpu_elt, elt_t)
    else:
      assert False, "Unsupported type in CUDA backend %s" % t 
      
  def list_to_host(self, host_values, gpu_values, types):
    for i, t in enumerate(types):
      host_value = host_values[i]
      gpu_value = gpu_values[i]
      self.to_host(host_value, gpu_value, t)
    

  """
  def visit_IndexReduce(self, expr):
    fn =  self.get_fn(expr.fn, qualifier = "device")
    combine = self.get_fn(expr.combine, qualifier = "device")
    if self.in_host():
      #
      # weave two device functions together into a  reduce kernel
      #
      pass 
 
  
  def visit_IndexScan(self, expr):
    fn =  self.get_fn(expr.fn, qualifier = "device")
    combine = self.get_fn(expr.combine, qualifier = "device")
    emit = self.get_fn(expr.emit, qualifier = "device")
    if self.in_host():
      pass 
  """


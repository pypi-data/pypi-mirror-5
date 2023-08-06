from treelike.testing_helpers import run_local_tests, expect_eq

import loopjit

def mk_identity(t):
  f, (x,), b = loopjit.build_fn([t], t)
  b.return_(x)
  return f

def identity_i64(x):
  fn = mk_identity(loopjit.Int64)
  print repr(fn) 
  return loopjit.run(fn, (x,))
  
def identity_f64(x):
  fn = mk_identity(loopjit.Float64)
  return loopjit.run(fn, (x,))

def test_identity():
  expect_eq(identity_i64(1), 1)
  expect_eq(identity_i64(-1), -1)
  expect_eq(identity_f64(1.0), 1.0)
  expect_eq(identity_f64(-1.0), -1.0)


if __name__ == '__main__':
 
  run_local_tests()  

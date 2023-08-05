Grain
=====

Overview
--------

Simple, extensible test assertions.

Usage
-----

Use `expect` to build test assertions.

```python
from grain import expect
from yourmodule import your_func

n = your_func(10)

# Raises an `AssertionError` if `n` is not equal to `100`.
expect(n).equal(100)

# Raises an `AssertionError` if `your_func(None)` does not raise a `TypeError`.
with expect.raises(TypeError):
    your_func(None)
```

Available assertion methods:

- expect(a).equal(b)
- expect(a).not_equal(b)
- expect(a).is_(b)
- expect(a).is_not(b)
- expect(a).true()
- expect(a).false()
- expect(a).in_(b)
- expect(a).not_in(b)
- expect(a).less(b)
- expect(a).less_equal(b)
- expect(a).greater(b)
- expect(a).greater_equal(b)
- expect(a).almost_equal(b)
- expect(a).not_almost_equal(b)
- expect.raises(exception_class)
- expect.fail()

Custom Assertions
-----------------

`expect` is actually just a class. You can use `expect.extend()` to conveniently
create a copy that mixes in additional methods. This lets you add custom
assertion methods that work exactly like the built-in methods.

The following code will replace `expect` with a new copy that includes two
additional `even` and `odd` assertion methods.

```python
from grain import expect

class CustomAssertions(object):
    def even(self):
        if self.actual % 2 == 0:
            return
        self.fail('Expected {} to be even'.format(repr(self.actual)))

    def odd(self):
        if self.actual % 2 != 0:
            return
        self.fail('Expected {} to be odd'.format(repr(self.actual)))

expect = expect.extend(CustomAssertions)

expect(2).even()
expect(3).odd()
```

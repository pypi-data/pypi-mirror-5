===========
Mini Test
===========

This project is inspired by Ruby minispec, but now it just implement some methods including:
  must_equal, must_true, must_equal_with_func, must_raise.

Using like the below:

if __name__ == '__main__':
    from minitest import *
    
    import operator
    with test_case("new test case"):


        with test("test must_equal"):
            'jc'.must_equal('jc')

        with test("test must_true"):
            True.must_true()
            False.must_true()


        with test("test must_equal_with_func"):
            (1).must_equal_with_func(1, operator.eq)
            (1).must_equal_with_func(2, operator.eq)

        def div_zero():
            1/0
            
        with test("test must_raise"):
            (lambda : div_zero()).must_raise(ZeroDivisionError)


The output will be:

Running tests:

.FF.

Finished tests in 0.021858s.

1) Failure:
The line No is [/Users/Colin/work/codes/python/minitest/test.py:13]:
--- expected
+++ actual
-[True]
#[False]

2) Failure:
The line No is [/Users/Colin/work/codes/python/minitest/test.py:18]:
--- expected
+++ actual
-[2]
#[1]

4 tests, 6 assertions, 2 failures, 0 errors.
[Finished in 0.1s]
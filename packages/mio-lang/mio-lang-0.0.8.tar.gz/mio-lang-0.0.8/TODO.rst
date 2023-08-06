TODO
====

- Fix bugs in the operator precedence parser:

::
    
    >>> x = tokenize("x < 5 and x > 2")
    >>> x
    'x < 5 ) and x > 2'
    
- Bring test coverage back up to 100%
- Figure out why ``from foo import *`` doesn't parse correctly.
- Figure out a way to avoid recursion so ``loop(print("foo"))`` works as expected.
- Rewrite factorial example like: ``Number fact = method((1..self) reduce(0, a, n, a * n))``
- Try to chnage the semantics of arguments such that:

  - Arguments are evaluated when blocks/methods are called.
  - A copy of unevaluated arguments are available in the message.

- Somehow work out a way to make applying of ``*args`` and/or ``**kwargs`` as well as everything else.

- Do a refresher on how to write an interpreter in RPython and write a really really simple one:

  - http://doc.pypy.org/en/latest/coding-guide.html#restricted-python
  - http://morepypy.blogspot.com.au/2011/04/tutorial-writing-interpreter-with-pypy.html

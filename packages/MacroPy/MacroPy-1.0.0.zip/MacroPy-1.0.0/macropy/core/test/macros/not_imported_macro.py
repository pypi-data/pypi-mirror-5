from macropy.core.macros import *

macros = Macros()

@macros.expr
def g(tree, **kw):
    return Num(n = 0)

@macros.expr
def f(tree, **kw):
    return Num(n = 0)
import unittest

from macropy.core.macros import *
from macropy.core.quotes import macros, q, u

class Tests(unittest.TestCase):
    def test_transform(self):
        tree = parse_expr('(1 + 2) * "3" + ("4" + "5") * 6')
        goal = parse_expr('((("1" * "2") + 3) * ((4 * 5) + "6"))')

        @Walker
        def transform(tree, **kw):
            if type(tree) is Num:
                return Str(s = str(tree.n))
            if type(tree) is Str:
                return Num(n = int(tree.s))
            if type(tree) is BinOp and type(tree.op) is Mult:
                return BinOp(tree.left, Add(), tree.right)
            if type(tree) is BinOp and type(tree.op) is Add:
                return BinOp(tree.left, Mult(), tree.right)

        assert unparse_ast(transform.recurse(tree)) == unparse_ast(goal)

    def test_collect(self):

        tree = parse_expr('(((1 + 2) + (3 + 4)) + ((5 + 6) + (7 + 8)))')
        total = [0]
        @Walker
        def sum(tree, collect, **kw):
            if type(tree) is Num:
                total[0] = total[0] + tree.n
                return collect(tree.n)

        tree, collected = sum.recurse_real(tree)
        assert total[0] == 36
        assert collected == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_ctx(self):
        tree = parse_expr('(1 + (2 + (3 + (4 + (5)))))')

        @Walker
        def deepen(tree, ctx, set_ctx, **kw):
            if type(tree) is Num:
                tree.n = tree.n + ctx
            else:
                return set_ctx(ctx + 1)

        new_tree = deepen.recurse(tree, ctx=0)
        goal = parse_expr('(2 + (4 + (6 + (8 + 9))))')
        assert unparse_ast(new_tree) == unparse_ast(goal)

    def test_stop(self):
        tree = parse_expr('(1 + 2 * 3 + 4 * (5 + 6) + 7)')
        goal = parse_expr('(0 + 2 * 3 + 4 * (5 + 6) + 0)')

        @Walker
        def stopper(tree, stop, **kw):
            if type(tree) is Num:
                tree.n = 0
            if type(tree) is BinOp and type(tree.op) is Mult:
                stop()

        new_tree = stopper.recurse(tree)
        assert unparse_ast(goal) == unparse_ast(new_tree)
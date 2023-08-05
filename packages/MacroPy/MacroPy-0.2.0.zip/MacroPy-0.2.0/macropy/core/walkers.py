from macropy.core import *
from macropy.core.util import *
from ast import *



class Walker(object):
    """
    Decorates a function of the form:

    @Walker
    def transform(tree, **kw):
        ...
        return new_tree


    Which is used via:

    new_tree = transform.recurse(old_tree, initial_ctx)
    new_tree = transform.recurse(old_tree)
    new_tree, collected = transform.recurse_real(old_tree, initial_ctx)
    new_tree, collected = transform.recurse_real(old_tree)

    The `transform` function takes the tree to be transformed, in addition to
    a set of `**kw` which provides additional functionality:

    - `ctx`: this is the value that is (optionally) passed in to the `recurse`
      and `recurse_real` methods.
    - `set_ctx`: this is a function, used via `set_ctx(new_ctx)` anywhere in
      `transform`, which will cause any children of `tree` to receive `new_ctx`
      as their `ctx` variable.
    - `collect`: this is a function used via `collect(thing)`, which adds
      `thing` to the `collected` list returned by `recurse_real`.
    - `stop`: when called via `stop()`, this prevents recursion on children
      of the current tree.

    These additional arguments can be declared in the signature, e.g.:

    @Walker
    def transform(tree, ctx, set_ctx, **kw):
        ... do stuff with ctx ...
        set_ctx(...)
        return new_tree

    for ease of use.
    """
    def __init__(self, func):
        self.func = func

    def walk_children(self, tree, ctx=None):
        if isinstance(tree, AST):
            aggregates = []

            for field, old_value in iter_fields(tree):
                old_value = getattr(tree, field, None)
                new_value, new_aggregate = self.recurse_real(old_value, ctx)
                aggregates.extend(new_aggregate)
                setattr(tree, field, new_value)

            return aggregates

        elif isinstance(tree, list) and len(tree) > 0:

            aggregates = []
            new_tree = []
            for t in tree:
                new_t, new_a = self.recurse_real(t, ctx)
                if type(new_t) is list:
                    new_tree.extend(new_t)
                else:
                    new_tree.append(new_t)
                aggregates.extend(new_a)

            tree[:] = new_tree
            return aggregates

        else:
            return []

    def recurse(self, tree, ctx=None):
        """Traverse the given AST and return the transformed tree."""
        return self.recurse_real(tree, ctx)[0]

    def recurse_real(self, tree, ctx=None):
        """Traverse the given AST and return the transformed tree together
        with any values which were collected along with way."""

        if isinstance(tree, AST):
            aggregates = []
            stop_now = [False]

            def stop():
                stop_now[0] = True

            new_ctx = [ctx]

            def set_ctx(new):
                new_ctx[0] = new

            # Provide the function with a bunch of controls, in addition to
            # the tree itself.
            new_tree = self.func(
                tree=tree,
                ctx=ctx,
                collect=aggregates.append,
                set_ctx=set_ctx,
                stop=stop
            )

            if new_tree is not None:
                tree = new_tree

            if not stop_now[0]:
                aggregates.extend(self.walk_children(tree, new_ctx[0]))

        else:
            aggregates = self.walk_children(tree, ctx)

        return tree, aggregates



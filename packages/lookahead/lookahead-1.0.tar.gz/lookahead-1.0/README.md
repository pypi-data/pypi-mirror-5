lookahead
=========

Constructs a generator over the iterable yielding look-ahead (and/or
“look-behind”) tuples. One tuple will be generated for each element value
accessible from the iterator, containing that element and the number of
elements specified just prior to and immediately after. When no such
element exists, the None is used instead.

If one were to think of iterator as a list, this is would be similar to
appending `[None]*lookahead` and prepending `[None]*lookbehind`, then
iterating over and returning a sliding window of length
`lookbehind+1+ lookahead` (except of course that instead of generating
the such a list, this implementation generates (and caches) lookahead
values only as needed).

lookahead() may be called with 1, 2, or 3 parameters:

    lookahead(iterable)
        Defaults to lookahead=1, lookbehind=0
    lookahead(iterable, lookahead)
        Defaults to lookbehind=0
    lookahead(iterable, lookbehind, lookahead)
        Notice that lookahead is now the 3rd parameter!

Example semantics:

    lookahead(iterable):
        yield (item, next)
    lookahead(iterable, 2):
        yield (item, next, next+1)
    lookahead(iterable, 1, 2):
        yield (prev, item, next, next+1)
    lookahead(iterable, p, n):
        yeild (prev, ..., prev+p-1, item, next, ..., next+n-1)

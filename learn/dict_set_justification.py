"""
pip install pyZFC
"""
from zfc import NaturalNumber

# Intersection of natural numbers corresponds to the minimum operation
NaturalNumber(130) & NaturalNumber(32)

# Union of natural numbers corresponds to the maximum operation
NaturalNumber(130) | NaturalNumber(32)

# Symmetric difference does not seem to correspond to a natural
NaturalNumber(5) ^ NaturalNumber(2)

# Set difference correponds to subtraction (that is clipped at zero)
NaturalNumber(130) - NaturalNumber(32)

# Successor is you unioned with the set containing you
assert NaturalNumber(130) | {NaturalNumber(130)} == set(NaturalNumber(131))


"""

Dict default definitions:

    union - rightmost values take priority by default
    symmetric_difference - rightmost values take priority by default

    difference - leftmost values take priority by default
    intersection - leftmost values take priority by default


Justifictions:

Notice that set-based union and symmetric_difference share an "additive" property, in that they can result in sets that are not subsets of any input.

In contrast, the set-based intersection and difference operations share a "subtractive" property. They always result in a set that is a subset of one of the inputs.

In this sense, a "additive" operation can expand into a never before seen set, whereas "subtrative" operations cannot do this.

An "additive" operation must consider all inputs because it is not guarenteed to see its **rightmost** input.

A "subtractive" operation's leftmost input will always be a superset of the result. You are guarenteed to have seen all possible elements that could be in the result after you have seen the **leftmost** input.

In the context where you are streaming inputs, so you see the "leftmost" element first and the "rightmost" last, and for "addative" operations you must wait until the rightmost until you are gaurenteed to have the information needed to allocate the output. For "subtractive" operations, you have all of the information you need immediately after you see the leftmost element.

The above is for pure sets. For dictionaries, one could invent any prioritization to define which values tag along with the keys.  However, I believe this "minimum number of items to allocate the output" is the "natural" default way to assign a value to each output key.

Imagine each of the union, intersection, difference, and symmetric_difference methods had a keyword argument: `merge`, which took an iterator of values, with the first being the leftmost and last being the rightmost candidate value for that key.

One could implement fancy things such as:  `merge=set` to take all values and produce a new dictionary with a set of all input values for that key.

Taking the leftmost would correspond to:


```python
def merge(values):
    return next(values)
```

And the rightmost would be:

    .. code::

```python
def merge(values):
    for v in values:
        ...
    return v
```

"""

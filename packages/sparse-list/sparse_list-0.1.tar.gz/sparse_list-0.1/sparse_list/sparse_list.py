#!/usr/bin/env python

import itertools


class SparseList(object):
    '''
    Inspired by http://stackoverflow.com/q/17522753/78845

    A "sparse list" is a list where most (say, more than 95% of) values will be
    None (or some other default)  and for reasons of memory efficiency you
    don't wish to store these (cf. Sparse array
    <http://en.wikipedia.org/wiki/Sparse_array>).

    This implementation has a similar interface to Python's built-in list but
    stores the data in a dictionary to conserve memory.

    See accompanying unit-tests for documentiation.
    '''

    def __init__(self, arg, default_value=None):
        self.default = default_value
        self.elements = {}
        if isinstance(arg, int):
            self.size = int(arg)
        elif isinstance(arg, dict):
            self.initialise_from_dict(arg)
        else:
            self.initialise_from_iterable(arg)

    def __len__(self):
        return self.size

    def __setitem__(self, index, value):
        self.elements[index] = value
        self.size = max(index + 1, self.size)

    def __getitem__(self, index):
        try:
            s = slice(index.start, index.stop, index.step).indices(self.size)
            return [self[i] for i in xrange(*s)]
        except AttributeError:
            i = slice(index).indices(self.size)[1]
            return self.elements.get(i, self.default)

    def __delitem__(self, index):
        try:
            del self.elements[index]
        except KeyError:
            pass

    def __delslice__(self, start, stop):
        map(self.__delitem__, xrange(start, stop))

    def __iter__(self):
        for index in xrange(self.size):
            yield self[index]

    def __contains__(self, index):
        return index in self.elements.itervalues()

    def __repr__(self):
        return '[{}]'.format(', '.join(map(str, self)))

    def __add__(self, other):
        result = self[:]
        return result.__iadd__(other)

    def __iadd__(self, other):
        map(self.append, other)
        return self

    def append(self, element):
        self.elements[self.size] = element
        self.size += 1

    push = append

    def initialise_from_dict(self, arg):
        def convert_and_size(key):
            try:
                key = int(key)
            except ValueError:
                raise ValueError('Invalid key: {}'.format(key))
            self.size = max(key + 1, self.size)
            return key
        self.size = 0
        self.elements = {convert_and_size(k): v for k, v in arg.iteritems()}

    def initialise_from_iterable(self, arg):
        self.elements = {k: v for k, v in enumerate(arg)}
        self.size = len(self.elements)

    def __eq__(self, other):
        return all(a == b for a, b in itertools.izip_longest(self, other))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return any(a < b for a, b in itertools.izip_longest(self, other))

    def __ge__(self, other):
        return not self.__lt__(other)

    def __mul__(self, multiplier):
        result = []
        for x in xrange(multiplier):
            result += self[:]
        return result

    def count(self, value):
        return sum(map(lambda v: v == value, self.elements.itervalues())) + (
            self.size - len(self.elements) if value == self.default else 0
        )

    def extend(self, iterable):
        self.__iadd__(iterable)

    def index(self, value):
        if value == self.default:
            for k, v in enumerate(self):
                if v == value:
                    return k
            return None
        for k, v in self.elements.iteritems():
            if v == value:
                return k
        return None

    def pop(self):
        value = self[-1]
        del self[-1]
        self.size -= 1
        return value

    def remove(self, value):
        if value == self.default:
            return
        for k, v in self.elements.iteritems():
            if v == value:
                del self.elements[k]
                return None
        raise ValueError('{} not in SparseList'.format(value))

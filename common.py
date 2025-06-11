"""
    Locate classes and patterns for all project
"""
import copy



class jsd(dict):
    def __init__(self, *args, **items):
        if len(args) == 1 and isinstance(args[0], dict):
            super(jsd, self).__init__(args[0])
        elif items and not args:
            super(jsd, self).__init__(items)
        else:
            super(jsd, self).__init__(*args)

    def __deepcopy__(self, memodict={}):
        return jsd.recurse(copy.deepcopy(dict(self),memo=memodict))

    def __copy__(self):
        return jsd(self)

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value
        return self

    @staticmethod
    def recurse(d):
        if isinstance(d, list):
            for i in range(len(d)):
                if isinstance(d[i], dict):
                    d[i] = jsd.recurse(d[i])
                if isinstance(d[i], list):
                    d[i] = jsd.recurse(d[i])
                if isinstance(d[i], tuple):
                    d[i] = jsd.recurse(d[i])
            return d
        elif isinstance(d, dict):
            a = jsd(d)
            for i in a.keys():
                if isinstance(a[i], dict):
                    a[i] = jsd.recurse(a[i])
                elif isinstance(a[i], list):
                    a[i] = jsd.recurse(a[i])
                elif isinstance(a[i], tuple):
                    a[i] = jsd.recurse(a[i])
            return a
        elif isinstance(d, tuple):
            a = [None] * len(d)
            for i in range(len(d)):
                if isinstance(d[i], dict):
                    a[i] = jsd.recurse(d[i])
                elif isinstance(d[i], list):
                    a[i] = jsd.recurse(d[i])
                elif isinstance(d[i], tuple):
                    a[i] = jsd.recurse(d[i])
                else:
                    a[i] = d[i]
            return tuple(a)
        return d

import copy
import inspect
import re
import warnings


class _Values(list):
    pass


def _is_collect(pattern):
    return (isinstance(pattern, Matcher) and not pattern.ignore)


def match(pattern, subject, flatten=True):
    # XXX: try to optimize this function
    def _match(pattern, subject, success):
        if not isinstance(pattern, tuple):
            values = _Values([subject] if _is_collect(pattern) else [])
            return (success and pattern == subject, values)
        else:
            values = _Values()
            subject_is_tuple = isinstance(subject, tuple)

            for subpattern in pattern:
                success, subvalues = _match(subpattern, subject[0] if subject_is_tuple and subject else None, success)

                assert isinstance(subvalues, _Values)
                values.extend(subvalues)

                subject = subject[1:] if subject_is_tuple and subject else None

            # if not all of the subject has been consumed, the match has failed:
            if subject:
                success = False

            return success, values

    success, values = _match(pattern, subject, True)
    assert isinstance(values, _Values)

    return ((success, tuple(values))
            if not flatten else
            (success if not values else (success,) + tuple(values)))


class _Marker(object):
    def __init__(self):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "%s(<unknown>)" % (type(self).__name__,)


class Matcher(_Marker):
    ignore = False

    def __new__(self, *args):
        obj = super(Matcher, self).__new__(self)

        try:
            argspec = inspect.getargspec(type(obj).__init__)
        except TypeError:
            return obj
        else:
            if argspec.varargs or argspec.keywords:
                return obj

        nargs = len(argspec.args) - 1
        if len(args) <= nargs:  # <= because for example (at least) copy.copy causes us to be called with no arguments
            return obj
        else:
            obj.__init__(*args[:nargs])
            return obj.__eq__(*args[nargs:])

    def __req__(self, x):
        return self.__eq__(x)

    def __or__(self, other):
        return OR(self, other)

    def __and__(self, other):
        return AND(self, other)

    def __ne__(self, x):
        return not (self == x)

    def __hash__(self):
        # detect when a matcher was used as a dict key, or put in a set or similar
        raise RuntimeError("Can't hash pattern matchers")


class ANY(Matcher):
    def __eq__(self, x):
        return True

    def __call__(self, *args, **kwargs):
        """Enables `ANY` to be used as a function that takes any arguments and always returns `True`."""
        return True

    def __str__(self):
        return 'ANY'
ANY = ANY()


def IGNORE(x):
    if isinstance(x, Matcher):
        x = copy.copy(x)
        x.ignore = True
    return x


class EQ(Matcher):
    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, x):
        return self.pattern == x

    def __str__(self):
        return 'EQ(%r)' % (self.pattern,)


class GT(Matcher):
    def __init__(self, value):
        self.value = value

    def __eq__(self, x):
        return x > self.value

    def __str__(self):
        return 'GT(%r)' % (self.value,)


class LT(Matcher):
    def __init__(self, value):
        self.value = value

    def __eq__(self, x):
        return x < self.value

    def __str__(self):
        return 'LT(%r)' % (self.value,)


class IS_INSTANCE(Matcher):
    def __init__(self, t):
        self.t = t

    def __eq__(self, x):
        return isinstance(x, self.t)

    def __str__(self):
        modname, clsname = self.t.__module__, self.t.__name__
        typename = (modname + '.' if modname != '__builtin__' else '') + clsname
        return 'IS_INSTANCE(%s)' % (typename)


class MATCH(Matcher):
    def __init__(self, fn):
        self.fn = fn

    def __eq__(self, x):
        return self.fn(x)

    def __str__(self):
        return 'MATCH(%s)' % self.fn


class NOT(Matcher):
    def __init__(self, matcher):
        self.matcher = matcher

    def __eq__(self, x):
        return self.matcher != x

    def __str__(self):
        return 'NOT(%s)' % self.matcher


class IF(Matcher):
    def __init__(self, cond, pattern):
        self.cond = cond
        self.pattern = pattern

    def __eq__(self, x):
        return self.cond() and x == self.pattern

    def __str__(self):
        # TODO: find a way to re-build the original source code from self.cond.func_code.co_code
        return 'IF(%s, %s)' % (self.cond, self.pattern)


class OR(Matcher):
    def __init__(self, *matchers):
        self.matchers = matchers

    def __eq__(self, x):
        return not self.matchers or any(matcher == x for matcher in self.matchers)

    def __str__(self):
        return ' | '.join(repr(x) for x in self.matchers)


class AND(Matcher):
    def __init__(self, matcher1, matcher2):
        self.matcher1, self.matcher2 = matcher1, matcher2

    def __eq__(self, x):
        return self.matcher1 == x and self.matcher2 == x

    def __str__(self):
        return '%s & %s' % (self.matcher1, self.matcher2)


class REGEXP(Matcher):
    def __init__(self, regexp):
        self.regexp = regexp

    def __eq__(self, other):
        return bool(re.match(self.regexp, other))

    def __str__(self):
        return str(self.regexp)


class IN(Matcher):
    def __init__(self, options):
        self.options = list(options)

    def __eq__(self, other):
        return other in self.options

    def __str__(self):
        return 'IN(%r)' % (self.options,)


class CONTAINS(Matcher):
    def __init__(self, elem):
        self.elem = elem

    def __eq__(self, other):
        w = self.elem
        if hasattr(other, '__contains__'):
            return w in other
        else:
            return False

    def __str__(self):
        return 'CONTAINS(%r)' % self.subset_or_elem


class HASSUBSET(Matcher):
    def __init__(self, items):
        self.items = items

    def __eq__(self, other):
        w = self.items
        if isinstance(w, (list, tuple)):
            for i in w:
                if i not in other:
                    return False
            return True
        elif isinstance(w, dict):
            for key, value in w.items():
                if other.get(key, object()) != value:
                    return False
            return True
        else:
            raise TypeError("a dict or a list is required")

    def __str__(self):
        return 'HASSUBSET(%r)' % self.items


def HASITEMS(*args, **kwargs):
    warnings.warn("HASITEMS has been deprecated in favor of HASSUBSET", DeprecationWarning)
    return HASSUBSET(*args, **kwargs)

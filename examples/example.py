class X(dict, object):
    def __init__(self, a):
        setattr(self, "a", a)

    def b(self):
        return self.a

a = X(5)
print(a.b())
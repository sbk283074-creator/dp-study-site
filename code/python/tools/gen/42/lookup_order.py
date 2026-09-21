class NonData:
    """Only __get__ -- a NON-data descriptor."""

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return "NonData.__get__ won"


class Data:
    """__get__ and __set__ -- a DATA descriptor."""

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get("_stored", "Data.__get__ won")

    def __set__(self, obj, value):
        obj.__dict__["_stored"] = f"stored by Data.__set__: {value}"


class Demo:
    non_data = NonData()
    data = Data()


d = Demo()

print("1. nothing on the instance yet -- the class is the only source")
print("   d.non_data ->", d.non_data)
print("   d.data     ->", d.data)
print()

print("2. now assign to both")
d.non_data = "plain instance attribute"
d.data = "assignment"
print("   d.__dict__ ->", d.__dict__)
print()

print("3. read them back")
print("   d.non_data ->", d.non_data, " <- the INSTANCE won")
print("   d.data     ->", d.data, " <- the DESCRIPTOR won")
print()
print("The only difference between the two classes is __set__.")
print("A data descriptor takes precedence over the instance dict.")
print("A non-data descriptor does not.")

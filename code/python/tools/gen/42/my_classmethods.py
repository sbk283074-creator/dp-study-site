from types import MethodType


class my_classmethod:
    """Binds the CLASS instead of the instance."""

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if objtype is None:
            objtype = type(obj)
        return MethodType(self.func, objtype)


class my_staticmethod:
    """Binds nothing at all -- returns the function unchanged."""

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        return self.func


class Temperature:
    unit = "C"

    def __init__(self, celsius):
        self.celsius = celsius

    @my_classmethod
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)

    @my_staticmethod
    def is_freezing(kelvin):
        return kelvin <= 273.15


t = Temperature.from_fahrenheit(212)
print("Temperature.from_fahrenheit(212) ->", round(t.celsius, 6), "degrees C")
print("it built a", type(t).__name__, "with no instance involved")
print()

print("my_classmethod bound the class, so `cls` is Temperature:")
print("  Temperature.unit ->", Temperature.unit)
print("  a subclass would be passed instead:")


class Fahrenheit(Temperature):
    unit = "F"


print("  Fahrenheit.from_fahrenheit(212).unit ->",
      Fahrenheit.from_fahrenheit(212).unit)
print()

print("my_staticmethod bound nothing, so there is no first argument:")
print("  Temperature.is_freezing(273.0) ->", Temperature.is_freezing(273.0))
print("  Temperature.is_freezing(300.0) ->", Temperature.is_freezing(300.0))
print("  Temperature(20).is_freezing(273.0) ->",
      Temperature(20).is_freezing(273.0))
print("  the last call went through an instance, and it made no difference")
print()

print("the built-ins behave identically:")
class Real:
    @classmethod
    def cm(cls):
        return cls.__name__

    @staticmethod
    def sm():
        return "no self, no cls"


print("  Real.cm()    ->", Real.cm(), "   Real().cm() ->", Real().cm())
print("  Real.sm()    ->", Real.sm())

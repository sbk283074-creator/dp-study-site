def log(msg):
    print("  " + msg)


class Meta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        log(f"1. __prepare__({name}) -> builds the namespace mapping")
        return {}

    def __new__(mcls, name, bases, namespace, **kwargs):
        log(f"2. Meta.__new__({name}) -> the class body has already run")
        public = sorted(k for k in namespace if not k.startswith("_"))
        log(f"   names the class body defined: {public}")
        log(f"   '__init__' is in the namespace: {'__init__' in namespace}")
        cls = super().__new__(mcls, name, bases, namespace)
        log("   (type.__new__ has now called __set_name__ on every descriptor)")
        return cls

    def __init__(cls, name, bases, namespace, **kwargs):
        log(f"3. Meta.__init__({name})")
        super().__init__(name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        log(f"4. Meta.__call__({cls.__name__}) -- this is what Widget() hits")
        return super().__call__(*args, **kwargs)


class Tracker:
    def __set_name__(self, owner, name):
        log(f"   __set_name__: {owner.__name__}.{name}")


log("about to execute the class statement")


class Widget(metaclass=Meta):
    log("   the class body is running")
    field = Tracker()
    kind = "widget"

    def __init__(self):
        log("   5. the instance __init__ runs")


log("the class statement is finished")
w = Widget()

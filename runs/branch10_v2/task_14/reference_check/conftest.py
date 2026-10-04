def pytest_collection_modifyitems(items):
    def own(item):
        mod = getattr(item, "module", None)
        obj = getattr(item, "obj", None)
        return mod is None or getattr(obj, "__module__", mod.__name__) == mod.__name__
    items[:] = [i for i in items if own(i)]

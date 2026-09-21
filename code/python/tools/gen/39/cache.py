import importlib.util, py_compile, sys
from pathlib import Path

print("the cache file a module would get:")
print("  ", importlib.util.cache_from_source("shop/pricing.py"))

print("\nsource suffix and magic:")
print("   sys.implementation.cache_tag:", sys.implementation.cache_tag)
print("   importlib.machinery.MAGIC_NUMBER:", importlib.util.MAGIC_NUMBER.hex())

import os, subprocess, sys, tempfile, textwrap

SOURCE = textwrap.dedent('''
    """Module docstring."""
    def f(x):
        """Function docstring."""
        assert x > 0, "x must be positive"
        return x * 2

    print("__debug__    =", __debug__)
    print("module doc   =", repr(__doc__))
    print("f.__doc__    =", repr(f.__doc__))
    print("f(-1)        =", f(-1))
''')

with tempfile.TemporaryDirectory() as td:
    path = os.path.join(td, "demo.py")
    with open(path, "w") as fh:
        fh.write(SOURCE)
    for flags in ([], ["-O"], ["-OO"]):
        label = "python3 " + " ".join(flags) if flags else "python3"
        print(f"--- {label}")
        proc = subprocess.run([sys.executable, *flags, path],
                              capture_output=True, text=True)
        print(proc.stdout.rstrip())
        if proc.stderr.strip():
            print("stderr:", proc.stderr.strip().splitlines()[-1])
        print()

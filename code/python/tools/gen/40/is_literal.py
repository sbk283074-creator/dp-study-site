import os, subprocess, sys, tempfile

SOURCE = "print(257 is 257)\n"

with tempfile.TemporaryDirectory() as td:
    path = os.path.join(td, "demo.py")
    with open(path, "w") as fh:
        fh.write(SOURCE)

    proc = subprocess.run([sys.executable, path], capture_output=True, text=True)

print("the program  : print(257 is 257)")
print("its stdout   :", proc.stdout.strip())
print("its stderr   :", proc.stderr.strip().splitlines()[0].split(": ", 1)[1])
print()
print("The interpreter rejected nothing -- the program ran and printed True.")
print("But the compiler noticed the mistake, and said so, before running it.")

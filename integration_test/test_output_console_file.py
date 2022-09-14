import sys

class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush() # If you want the output to be visible immediately
    def flush(self) :
        for f in self.files:
            f.flush()

f = open('out.txt', 'w')
original = sys.stdout
sys.stdout = Tee(sys.stdout, f)
print("This will go to both std out and the file")  # This will go to stdout and the file out.txt

a = 2345
print(f"a = {a}")

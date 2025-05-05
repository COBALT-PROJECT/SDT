from sse2 import listen_to_digitaltwins

# Create a dummy object with a reference to the function
class DummyObject:
    def __init__(self):
        self.listen_to_digitaltwins = listen_to_digitaltwins

# Create instance and run
if __name__ == "__main__":
    dummy = DummyObject()
    dummy.listen_to_digitaltwins(dummy)
class ClassA:
    def __init__(self, a):
        self.a = a
        print("ClassA init")

class ClassB:
    def __init__(self, b):
        self.b = b
        print("ClassB init")

class CombinedClass(ClassA, ClassB):
    def __init__(self, a, b, c):
        super().__init__(a)  # Call __init__ of ClassA
        super().__init__(b)  # Call __init__ of ClassB
        self.c = c
        print("CombinedClass init")

# Create an instance of CombinedClass
combined_instance = CombinedClass('A-value', 'B-value', 'C-value')

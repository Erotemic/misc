class MyValue:
    def __init__(self, value):
        self.value = value

    def __pow__(self, arg):
        print('EXECUTE OP')
        return self.__class__(self.value ** arg)


def main():
    x = MyValue(3)
    [i for i in range(10) if x ** 3]

if __name__ == '__main__':
    main()

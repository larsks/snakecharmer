def F2C(temp):
    return (temp - 32) * (5/9)


def C2F(temp):
    return temp * (9/5) + 32


def file_exists(path):
    try:
        with open(path, 'r'):
            return True
    except OSError:
        return False

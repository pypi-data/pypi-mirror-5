from widgets import FullScreenTextarea
version = (1, 1)


def get_version():
    """returns a pep complient version number"""
    return '.'.join(str(i) for i in version)

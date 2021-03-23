class MissingContentException(Exception):
    """ This is essentially a generic 404. """
    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "MissingContentException"

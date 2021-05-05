class PathConverter:
    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class NumericConverter(PathConverter):
    regex = r'[\d]+'


class SubpartConverter(PathConverter):
    regex = r'[Ss]ubpart-[A-Za-z]'

    def to_python(self, value):
        return value[0].upper() + value[1:-1] + value[-1].upper()


class VersionConverter(PathConverter):
    regex = r'[\d\w]+-[\d\w]+(?:-\d+)?'

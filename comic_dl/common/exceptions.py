
class InvalidRangeException(Exception):
    ...


class ComicDoesNotExist(Exception):
    msg = 'The alias specified is not related with any comic in the database,'\
        ' add comic with comic_dl --add="<query>" to set alias'

    def __init__(self, msg=msg, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class AliasNotSpecified(Exception):
    ...


class PlatformNotSupported(Exception):
    ...

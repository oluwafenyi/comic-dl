
class InvalidRangeException(Exception):
    ...


class AliasDoesNotExist(Exception):
    msg = 'The alias specified does not exist in the database, '\
        'add comic with comic_dl --add="<query>" to set alias'

    def __init__(self, msg=msg, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)

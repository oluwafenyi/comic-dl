
class InvalidRangeException(Exception):
    ...


class PlatformNotSupported(Exception):
    ...


class ArgumentNotSpecified(Exception):
    ...


class ComicDoesNotExist(Exception):
    msg = 'The alias specified is not related with any comic in the database,'\
        ' add comic with comic_dl --add="<query>" to set alias'

    def __init__(self, msg=msg, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class AliasNotSpecified(ArgumentNotSpecified):
    msg = 'Positional argument alias not specified'

    def __init__(self, msg=msg, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class IssueNotAvailable(Exception):
    msg = 'The issue specified has not been released.'

    def __init__(self, msg=msg, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class NetworkError(Exception):
    msg = 'No internet connection available or page not found.'

    def __init__(self, msg=msg, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class CAPTCHAError(Exception):
    msg = 'The site brought out a captcha, please wait for some time before' +\
          ' trying again.'

    def __init__(self, msg=msg, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)

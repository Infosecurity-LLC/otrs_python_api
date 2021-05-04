class OTRSException(Exception):
    pass


class HTTPMethodNotSupportedError(OTRSException):
    pass


class OTRSBadResponse(OTRSException):
    pass


class AuthError(OTRSException):
    pass


class AccessDeniedError(OTRSException):
    pass


class InvalidParameterError(OTRSException):
    pass


class ArgumentMissingError(Exception):
    pass


class ArgumentInvalidError(Exception):
    pass


class InvalidInitArgument(Exception):
    pass


class InvalidTicketGetArgument(Exception):
    pass


class InvalidTicketCreateArgument(Exception):
    pass


class InvalidTicketUpdateArgument(Exception):
    pass

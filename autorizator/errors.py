"""Autorizator Errors"""


class AutorizatorError(Exception):
    """Base Class for Autorizator Errors"""

    pass


class AutorizatorRuntimeError(Exception):
    """Base Class for expected wrong program states"""

    pass


class AutorizatorLogicError(Exception):
    """Base Class for errors caused by invalid code"""

    pass

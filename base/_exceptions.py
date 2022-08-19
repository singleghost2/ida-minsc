import sys, builtins as E

class UnicodeException(E.BaseException):
    """
    A base exception that handles converting a unicode message
    into its UTF-8 form so that it can be emitted using Python's
    standard console.

    Copied from Python 2.7.15 implementation.
    """
    # tp_init
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

    # Python2 can be emitted in more than one way which requires us
    # to implement both the Exception.__str__ and Exception.__unicode__
    # methods. If returning a regular string (bytes), then we need to
    # utf-8 encode the result because IDA's console will automatically
    # decode it.
    if sys.version_info.major < 3:

        # tp_str
        def __str__(self):
            length = len(self.args)
            if length == 0:
                return ""
            elif length == 1:
                item = self.args[0]
                return str(item.encode('utf8') if isinstance(item, unicode) else item)
            return str(self.args)

        def __unicode__(self):
            # return unicode(self.__str__())
            length = len(self.args)
            if length == 0:
                return u""
            elif length == 1:
                return unicode(self.args[0])
            return unicode(self.args)

    # Python3 really only requires us to implement this method when
    # emitting an exception. This is the same as a unicode type, so
    # we should be okay with casting the exception's arguments.
    else:

        # tp_str
        def __str__(self):
            length = len(self.args)
            if length == 0:
                return ""
            elif length == 1:
                item = self.args[0]
                return str(item)
            return str(self.args)

    # tp_repr
    def __repr__(self):
        repr_suffix = repr(self.args)
        name = type(self).__name__
        dot = name.rfind('.')
        shortname = name[1 + dot:] if dot > -1 else name
        return shortname + repr_suffix

    # tp_as_sequence
    def __iter__(self):
        for item in self.args:
            yield item
        return

    # tp_as_sequence
    def __getitem__(self, index):
        return self.args[index]
    def __getslice__(self, *indices):
        res = slice(*indices)
        return self.args[res]

    # tp_getset
    @property
    def message(self):
        return self.__message__
    @message.setter
    def message(self, message):
        # self.__message__ = "{!s}".format(message)
        self.__message__ = message
    @property
    def args(self):
        return self.__args__
    @args.setter
    def args(self, args):
        self.__args__ = tuple(item for item in args)

    # tp_methods
    def __reduce__(self):
        return self.args
    def __setstate__(self, pack):
        self.args = pack

class MissingTagError(E.KeyError, UnicodeException):
    """
    The requested tag at the specified address does not exist.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class MissingFunctionTagError(MissingTagError):
    """
    The requested tag for the specified function does not exist.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class MissingMethodError(E.NotImplementedError, UnicodeException):
    """
    A method belonging to a superclass that is required to be overloaded was called.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class MissingNameError(E.NameError, UnicodeException):
    """
    A name that was required was found missing and was unable to be recovered.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class UnsupportedVersion(E.NotImplementedError, UnicodeException):
    """
    This functionality is not supported on the current version of IDA.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class UnsupportedCapability(E.NotImplementedError, E.EnvironmentError, UnicodeException):
    """
    An unexpected or unsupported capability was specified.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class ResultMissingError(E.LookupError, UnicodeException):
    """
    The requested item is missing from its results.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class SearchResultsError(ResultMissingError):
    """
    No results were found.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class DisassemblerError(E.EnvironmentError, UnicodeException):
    """
    An api call has thrown an error or was unsuccessful.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class MissingTypeOrAttribute(E.TypeError, UnicodeException):
    """
    The specified location is missing some specific attribute or type.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class InvalidTypeOrValueError(E.TypeError, E.ValueError, UnicodeException):
    """
    An invalid value or type was specified.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class InvalidParameterError(E.AssertionError, InvalidTypeOrValueError):
    """
    An invalid parameter was specified by the user.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class OutOfBoundsError(E.ValueError, UnicodeException):
    """
    The specified item is out of bounds.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class AddressOutOfBoundsError(E.ArithmeticError, OutOfBoundsError):
    """
    The specified address is out of bounds.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class IndexOutOfBoundsError(E.IndexError, E.KeyError, OutOfBoundsError):
    """
    The specified index is out of bounds.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class ItemNotFoundError(E.KeyError, ResultMissingError):
    """
    The specified item or type was not found.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class FunctionNotFoundError(ItemNotFoundError):
    """
    Unable to locate the specified function.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class AddressNotFoundError(ItemNotFoundError):
    """
    Unable to locate the specified address.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class SegmentNotFoundError(ItemNotFoundError):
    """
    Unable to locate the specified segment.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class StructureNotFoundError(ItemNotFoundError):
    """
    Unable to locate the specified structure.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class EnumerationNotFoundError(ItemNotFoundError):
    """
    Unable to locate the specified enumeration.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class MemberNotFoundError(ItemNotFoundError):
    """
    Unable to locate the specified structure or enumeration member.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class RegisterNotFoundError(ItemNotFoundError):
    """
    Unable to locate the specified register.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class NetNodeNotFoundError(ItemNotFoundError):
    """
    Unable to locate the specified netnode.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class ReadOrWriteError(E.IOError, E.ValueError, UnicodeException):
    """
    Unable to read or write the specified number of bytes .
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class InvalidFormatError(E.KeyError, E.ValueError, UnicodeException):
    """
    The specified data has an invalid format.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class SerializationError(E.ValueError, E.IOError, UnicodeException):
    """
    There was an error while trying to serialize or deserialize the specified data.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class SizeMismatchError(SerializationError):
    """
    There was an error while trying to serialize or deserialize the specified data due to its size not matching.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class UnknownPrototypeError(E.LookupError, UnicodeException):
    """
    The requested prototype does not match any of the ones that are available.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

class DuplicateItemError(E.NameError, UnicodeException):
    """
    The requested command has failed due to a duplicate item.
    """
    def __init__(self, *args):
        self.__args__ = args
        self.__message__ = args[0] if len(args) == 1 else ''

#structure:742 and previous to it should output the module name, classname, and method
#comment:334 should catch whatever tree.find raises
#comment:100 (this needs some kind of error when the symbol or token component is not found)
#interface:283, interface:302, interface:620, interface:640 (this should be a NameError)

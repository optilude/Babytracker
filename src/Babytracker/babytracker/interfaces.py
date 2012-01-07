from zope.interface import Interface
from zope import schema

# Request markers

class IMobileRequest(Interface):
    """A request from a mobile browser
    """

class IDesktopRequest(Interface):
    """A request form a desktop browser
    """

# Entry markers

class IEntry(Interface):
    """
    """

    baby = schema.Object()

    start = schema.Datetime()
    end = schema.Datetime(required=False)

    note = schema.TextLine(required=False)

class IBreastFeed(IEntry):
    """
    """

    duration = schema.Time(required=False)

class IBottleFeed(IEntry):
    """
    """

    amount = schema.Int(required=False)

class IMixedFeed(IEntry):
    """
    """

    duration = schema.Time(required=False)
    amount = schema.Int(required=False)

class INappy(IEntry):
    """
    """

    note = schema.TextLine(required=False)

class ISleep(IEntry):
    """
    """

    duration = schema.Time(required=False)
    note = schema.TextLine(required=False)

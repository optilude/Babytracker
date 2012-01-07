from zope.interface import Interface

# Request markers

class IMobileRequest(Interface):
    """A request from a mobile browser
    """

class IDesktopRequest(Interface):
    """A request form a desktop browser
    """

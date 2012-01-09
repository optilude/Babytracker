from zope.interface import Interface

# Constants

VIEW_PERMISSION = 'view'
EDIT_PERMISSION = 'edit'
SIGNUP_PERMISSION = 'signup'

# Request markers

class IMobileRequest(Interface):
    """A request from a mobile browser
    """

class IDesktopRequest(Interface):
    """A request form a desktop browser
    """

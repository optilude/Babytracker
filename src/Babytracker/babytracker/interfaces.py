from zope.interface import Interface

# Constants

VIEW_PERMISSION = 'view'
EDIT_PERMISSION = 'edit'
SIGNUP_PERMISSION = 'signup'

# Interfaces

class IJSONCapable(Interface):
    """Models which can be converted to JSON data
    """

    def to_json_dict():
        """Return a dict representing this object as JSON
        """

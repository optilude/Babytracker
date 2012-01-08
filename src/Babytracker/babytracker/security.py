from babytracker.models import DBSession, User

def validate_user(userid, request):
    """Ensure the given user exists
    """

    session = DBSession()
    user = session.query(User).filter_by(email=userid).first()
    if user is not None:
        return (user.__name__,)
    return None

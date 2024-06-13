from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.authentication.transport.cookie import CookieTransport
from fastapi_users.authentication import JWTStrategy
from database import User
from auth.manager import get_user_manager

cookie_transport = CookieTransport(cookie_name='cookie_data', cookie_max_age=3600)

SECRET = 'SECRET'

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name='jwt',
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

def get_current_user():
    current_user = fastapi_users.current_user()
    return current_user


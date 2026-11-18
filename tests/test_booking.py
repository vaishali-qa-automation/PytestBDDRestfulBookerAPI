from pytest_bdd import scenarios
from steps.booking_steps import *   # noqa: F401,F403  — imported so step functions are registered

scenarios("../features/booking.feature")
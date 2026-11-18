from pytest_bdd import given, when, then
from faker import Faker
from datetime import date, timedelta
from models.booking import BookingData, BookingDates
from utilities.assertions_helper import assert_status_code, assert_matches_schema
from utilities.schemas import CREATE_BOOKING_RESPONSE_SCHEMA
import logging

logger = logging.getLogger(__name__)

fake = Faker()

@given("a guest wants to book a random stay")
def prepare_random_booking(context):
    checkin = date.today() + timedelta(days=5)
    checkout = checkin + timedelta(days=3)

    context["booking_data"] = BookingData(
        firstname=fake.first_name(),
        lastname=fake.last_name(),
        total_price=fake.random_int(min=50, max=500),
        booking_date=BookingDates(checkin=checkin, checkout=checkout),
        deposit_paid=fake.boolean()
    )
    logger.info(f"Random payload {context["booking_data"]} created for booking")

@when("the booking is created")
def create_booking(booking_api, context):
    payload = context["booking_data"].to_payload()
    logger.info(f"Creating a booking with payload {payload}")
    context["response"] = booking_api.create_booking(payload)
    context["booking_id"] = context["response"].json().get("bookingid")
    logger.info(f"Created booking with id {context["booking_id"]}")

@then("the booking is created successfully")
def check_created(context):
    logger.info(f"Verifying the created booking")
    assert_status_code(context["response"], 200)
    assert context["booking_id"] is not None, "Expected a booking id, got None"

@when("the booking is retrieved")
def get_booking(booking_api, context):
    logger.info(f"Retrieving the booking with id {context["booking_id"]}")
    context["response"] = booking_api.get_booking(context["booking_id"])
    logger.info(f"Retrieved Booking details {context['response']}")

@then("retrieving the booking returns the same guest details")
def check_guest_details(booking_api, context):
    logger.info("Verifying the guest details")
    get_booking(booking_api, context)   # trigger the GET, then assert below
    body = context["response"].json()
    expected = context["booking_data"]

    assert body["firstname"] == expected.firstname, (
        f"Expected firstname '{expected.firstname}', got '{body['firstname']}'"
    )
    assert body["lastname"] == expected.lastname, (
        f"Expected lastname '{expected.lastname}', got '{body['lastname']}'"
    )

@then("the booking response matches the expected schema")
def check_schema(context):
    logger.info("Verifying the created booking schema")
    assert_matches_schema(context["response"], CREATE_BOOKING_RESPONSE_SCHEMA)
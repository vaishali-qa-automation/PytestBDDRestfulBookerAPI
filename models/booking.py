from  dataclasses import dataclass
from datetime import date

@dataclass
class BookingDates:
    checkin: date
    checkout: date

    def to_payload(self) -> dict:
        return {
            "checkin": self.checkin.strftime("%Y-%m-%d"),
            "checkout": self.checkout.strftime("%Y-%m-%d"),
        }

@dataclass
class BookingData:
    firstname: str
    lastname: str
    total_price: int
    booking_date: BookingDates
    deposit_paid: bool
    additional_needs: str = ""

    def to_payload(self) -> dict:
        return {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "totalprice": self.total_price,
            "bookingdates": self.booking_date.to_payload(),   # delegate to nested dataclass
            "depositpaid": self.deposit_paid,
            "additionalneeds": self.additional_needs,
        }







import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3 import Retry
import logging

logger = logging.getLogger(__name__)

class BookingAPI:
    """
    This class has methods specific to booking API
    """

    def __init__(self, base_url, username, password):
        self._base_url = base_url
        self._token = None
        self.username = username
        self.password = password
        self._session = requests.Session()

        retry = Retry(
            total=4,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.headers.update({'Content-Type': 'application/json'})
        self._session.mount('https://', adapter)
        self._session.mount('http://', adapter)

    def _auth_headers(self, extra: dict | None = None) -> dict:
        headers = {'Cookie': f'token={self._token}', 'Accept': 'application/json'}
        if extra:
            headers.update(extra)
        return headers

    def create_token(self) -> None:
        """Authenticates and stores the session token."""
        url = f'{self._base_url}/auth'
        logger.info("Creating token with username and password")
        response = self._session.post(
            url, json={'username': self.username, 'password': self.password}
        )
        response.raise_for_status()
        logger.info("Successfully created token")
        self._token = response.json()['token']

    def get_bookings(self, query_params= None) -> Response:
        """
        This method returns the complete list of bookings based on provided query parameters
        Args:
            query_params: dictionary with query parameters

        Returns: Response object

        """
        logger.info(f"Getting bookings with query parameters {query_params}")
        url = f'{self._base_url}/booking'
        response = self._session.get(url, params=query_params)
        logger.info(f"Successfully retrieved bookings with query parameters {query_params}")
        logger.info(f"Response object: {response}")
        return response

    def get_booking(self, booking_id: int) -> Response:
        """
        This method gets the booking details of a specific booking
        :return: Response object
        Args:
            booking_id: specific booking id

        Returns:

        """
        logger.info(f"Getting booking details with booking id {booking_id}")
        url = f"{self._base_url}/booking/{booking_id}"
        response = self._session.get(url)
        logger.info(f"Successfully retrieved booking details with booking id {booking_id}")
        logger.info(f"Response object: {response}")
        return response

    def create_booking(self, payload: dict) -> Response:
        """
        This method creates a new booking
        Args:
            payload: models in dictionary format to create booking

        Returns: Response object

        """
        logger.info(f"Creating new booking with payload {payload}")
        url = self._base_url + '/booking'
        response = self._session.post(url, json=payload)
        logger.info(f"Successfully created booking with payload {payload}")
        logger.info(f"Response object: {response}")
        return response

    def update_booking(self, booking_id: int, payload: dict)-> Response:
        """
        This method updates the booking details with complete booking models
        Args:
            booking_id: booking id for details need to be updated
            payload:models in dictionary format to update booking details

        Returns: response object

        """
        logger.info(f"Updating booking details with booking id {booking_id}")
        url = f'{self._base_url}/booking/{booking_id}'
        response =  self._session.put(url, json=payload, headers=self._auth_headers())
        logger.info(f"Successfully updated booking details with booking id {booking_id}")
        logger.info(f"Response object: {response}")
        return response

    def partial_update_booking(self,booking_id, payload) -> Response:
        """
        This method updates the booking details with partial models
        Args:
            booking_id:booking id for details need to be updated
            payload: models in dictionary format to update some booking details

        Returns: Response object

        """
        logger.info(f"Updating booking details with booking id {booking_id}")
        url = f'{self._base_url}/booking/{booking_id}'
        response = self._session.patch(url, json=payload, headers=self._auth_headers())
        logger.info(f"Successfully updated booking details with booking id {booking_id}")
        logger.info(f"Response object: {response}")
        return response

    def delete_booking(self, booking_id) -> Response:
        """
        This method deletes the specific booking
        Args:
            booking_id: booking id to delete specific booking

        Returns: Response object

        """
        logger.info(f"Deleting booking with booking id {booking_id}")
        headers = {'Cookie': self._token}
        url = self._base_url + '/booking/' + booking_id
        response = self._session.delete(url, headers=headers)
        logger.info(f"Successfully deleted booking with booking id {booking_id}")
        logger.info(f"Response object: {response}")
        return response

    def close_session(self) -> None:
        """
        This method closes the session
        Returns: None

        """
        logger.info("Closing session")
        self._session.close()
import re
from bs4 import BeautifulSoup
from error import BookingServiceError
from service import raven_service
from model.booking import Booking
from model.event import Event

BOOKING_SERVICE_URL = 'https://www.mealbookings.cai.cam.ac.uk/index.php'


def get_available_events():
    """ Find all available events.
    :return: list of Event instances, representing events that exist in the
        booking system
    """
    browser = raven_service.get_default_authenticated_browser()
    hall_html = browser.open(BOOKING_SERVICE_URL).read()
    hall_soup = BeautifulSoup(hall_html)

    events = []
    events_table = hall_soup.find_all('table', {"class": "list"})[1]
    for event_row in events_table.find_all('td'):
        event_name = event_row.get_text()
        event_links = event_row.find_all('a')
        if len(event_links) > 0:
            event_link = event_links[0].get('href')
            event_code = int(re.search('\d+', event_link).group(0))
            events.append(Event(code=event_code, name=event_name))
    return events


def get_attendee_names(event, date):
    """ Find the names of people attending `event` on `date`.
    :param event: Event instance specifying event to check
    :param date: datetime.date instance specifying the date to check
    :return: list of Strings (names of attendees)
    :raises: BookingServiceError if `event` isn't occurring on `date`
    """
    def get_attendee_name(attendee_cell):
        """
        :return: the name encapsulated within `attendee_cell`, or None
        """
        attendee_text = attendee_cell.get_text()
        if len(attendee_text) > 0 and attendee_text[0] != '(':
            return attendee_text
        return None

    if not is_event_occurring(event, date):
        error_string = '%s not occurring on %s' % (str(event), str(date))
        raise BookingServiceError(error_string)

    browser = raven_service.get_default_authenticated_browser()
    event_url = event.url_for_date(date, BOOKING_SERVICE_URL)
    event_html = browser.open(event_url).read()
    event_soup = BeautifulSoup(event_html)

    attendance_table = event_soup.find_all('table', {'class': 'list'})[0]
    attendee_cells = attendance_table.find_all('td')
    attendee_names = map(get_attendee_name, attendee_cells)
    return [attendee for attendee in attendee_names if attendee is not None]


def is_event_occurring(event, date):
    """ Ensure that `event` is occurring on `date`.
    :param event: Event instance representing the event to check
    :param date: datetime.date for the date to check
    :return: bool, True if `event` is occurring on `date`
    """
    browser = raven_service.get_default_authenticated_browser()
    event_url = event.url_for_date(date, BOOKING_SERVICE_URL)
    event_html = browser.open(event_url).read()
    return 'not running on' not in event_html


def create_booking(event, user, date):
    """ Attempt to book `user` into `event` on `date`.
    :param event: Event instance for event to book in to
    :param user: User instance for person to book in
    :param date: datetime.date instance for date to book
    :return: Booking instance representing the successful booking
    :raises: BookingServiceError if the booking could not be made
    """
    if not is_event_occurring(event, date):
        error_string = '%s not occurring on %s' % (str(event), str(date))
        raise BookingServiceError(error_string)

    crsid, password = user.crsid, user.password
    browser = raven_service.get_authenticated_browser(crsid, password)
    event_url = event.url_for_date(date, BOOKING_SERVICE_URL)
    event_html = browser.open(event_url).read()
    if 'Other dietary or non-dietary requirements' not in event_html:
        # Not currently booked in, so make booking.
        browser.select_form(nr=0)
        browser.submit()
        browser.select_form(nr=0)
        browser.submit()
    return Booking(event, user, date)
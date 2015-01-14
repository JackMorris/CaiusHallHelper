import re
from bs4 import BeautifulSoup
from error import BookingServiceError
from model.booking import Booking
from model.event import Event
from service import raven_service

BOOKING_SERVICE_URL = 'https://www.mealbookings.cai.cam.ac.uk/index.php'

_AVAILABLE_EVENTS_CACHE = None
_ATTENDEE_NAME_CACHE = {}
_MENU_TEXT_CACHE = {}
_EVENT_OCCURRING_CACHE = {}


def get_available_events():
    """ Find all available events.
    :return: list of Event instances, representing events that exist in the
        booking system
    """
    global _AVAILABLE_EVENTS_CACHE
    if _AVAILABLE_EVENTS_CACHE is None:
        _AVAILABLE_EVENTS_CACHE = []
        browser = raven_service.get_default_authenticated_browser()
        hall_html = browser.open(BOOKING_SERVICE_URL).read()
        hall_soup = BeautifulSoup(hall_html)

        events_table = hall_soup.find_all('table', {"class": "list"})[1]
        for event_row in events_table.find_all('td'):
            event_name = event_row.get_text()
            event_links = event_row.find_all('a')
            if len(event_links) > 0:
                event_link = event_links[0].get('href')
                event_code = int(re.search('\d+', event_link).group(0))
                event = Event(code=event_code, name=event_name)
                _AVAILABLE_EVENTS_CACHE.append(event)
    return _AVAILABLE_EVENTS_CACHE[:]


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

    cache_key = (event.code, date)
    if cache_key not in _ATTENDEE_NAME_CACHE:
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
        attendee_names = [name for name in attendee_names if name is not None]
        _ATTENDEE_NAME_CACHE[cache_key] = attendee_names
    return _ATTENDEE_NAME_CACHE[cache_key][:]


def get_menu_text(event, date):
    """ Get the text for the menu for `event` on `date`.
    :param event: Event instance indicating the event to check the menu for
    :param date: datetime.date instance indicate which day to check
    :return: String containing the menu (newlines separating items), or None if
        no menu is found
    :raises: BookingServiceError is `event` isn't occurring on `date`
    """
    cache_key = (event.code, date)
    if cache_key not in _MENU_TEXT_CACHE:
        if not is_event_occurring(event, date):
            error_string = '%s not occurring on %s' % (str(event), str(date))
            raise BookingServiceError(error_string)
        browser = raven_service.get_default_authenticated_browser()
        event_url = event.url_for_date(date, BOOKING_SERVICE_URL)
        event_html = browser.open(event_url).read()
        event_soup = BeautifulSoup(event_html)

        menu_divs = event_soup.find_all('div', {'class': 'menu'})
        if len(menu_divs) == 0:
            return None
        menu_text = menu_divs[0].get_text().replace('\r', '\n')

        # Menu text sometimes contains large spans of ' ', so remove them. Also
        # remove stray spaces at the start/end of a line.
        menu_text = re.sub(r'  +', '', menu_text)
        menu_text = re.sub(r' ?\n ?', r'\n', menu_text)
        menu_text = re.sub(r'(^\n)|(\n$)', r'', menu_text)
        _MENU_TEXT_CACHE[cache_key] = menu_text
    return _MENU_TEXT_CACHE[cache_key]


def is_event_occurring(event, date):
    """ Ensure that `event` is occurring on `date`.
    :param event: Event instance representing the event to check
    :param date: datetime.date for the date to check
    :return: bool, True if `event` is occurring on `date`
    """
    cache_key = (event.code, date)
    if cache_key not in _EVENT_OCCURRING_CACHE:
        browser = raven_service.get_default_authenticated_browser()
        event_url = event.url_for_date(date, BOOKING_SERVICE_URL)
        event_html = browser.open(event_url).read()
        event_occurring = 'not running on' not in event_html
        _EVENT_OCCURRING_CACHE[cache_key] = event_occurring
    return _EVENT_OCCURRING_CACHE[cache_key]


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


def get_booking(event, user, date):
    """ Determine if `user` is booked into `event` on `date`.
    :param event: Event instance for event to check
    :param user: User instance for user to check
    :param date: datetime.date instance for date to check
    :return: Booking instance for booking if `user` is booked in to `event`,
        or None if not
    :raises: BookingServiceError if `event` doesn't take place on `date`.
    """
    if not is_event_occurring(event, date):
        error_string = '%s not occurring on %s' % (str(event), str(date))
        raise BookingServiceError(error_string)

    crsid, password = user.crsid, user.password
    browser = raven_service.get_authenticated_browser(crsid, password)
    event_url = event.url_for_date(date, BOOKING_SERVICE_URL)
    event_html = browser.open(event_url).read()
    if 'Other dietary or non-dietary requirements' in event_html:
        return Booking(event, user, date)
    return None
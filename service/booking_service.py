import re
from bs4 import BeautifulSoup
from service import raven_service
from model.event import Event

BOOKING_SERVICE_URL = 'https://www.mealbookings.cai.cam.ac.uk/'


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
import re


class Booking:
    """ A Booking represents a booking for an event that has been made. """

    def __init__(self, event, user, date):
        """ Construct a new booking.
        :param event: Event instance for the event that's booked in to
        :param user: User instance for the user that's booked in
        :param date: datetime.date instance for the day of the booking
        """
        self._event = event
        self._user = user
        self._date = date

    @property
    def event(self):
        return self._event

    @property
    def user(self):
        return self._user

    @property
    def date(self):
        return self._date

    def html_report(self, menu_text):
        """ Generate a HTML report for this booking, containing the event's
        menu (if one exists).
        :param menu_text: String containing text for the menu, or None if no
            menu exists
        :return: String containing the generated HTML
        """
        report_html = "<u><b>%s:</b></u><br /><br />" % self.event.name
        if menu_text is None:
            report_html += r'(no menu found)'
        else:
            menu_html = re.sub(r'\n', r'<br />', menu_text)
            report_html += menu_html
        report_html += r'<br /><br />'
        return report_html

    def __str__(self):
        """
        :return: String representation of this booking, in the format
            '<user> - <date> - <event>'
        """
        return '%s - %s - %s' % (self._user, self._date, self._event)
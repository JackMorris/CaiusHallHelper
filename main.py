from service import raven_service, email_service
from datetime import date, timedelta
from configuration import Configuration
import sys


def main():
    configuration_file_path = sys.argv[1]
    configuration = Configuration(configuration_file_path)
    _authenticate_services(configuration)
    _make_user_bookings(configuration.users, 3)
    _send_user_reports(configuration.users, 0)


def _authenticate_services(configuration):
    """ Use `configuration` to authenticate raven_service and email_service.
    :param configuration: Configuration instance for system configuration
    """
    raven_service.set_default_credentials(configuration.default_crsid,
                                          configuration.default_password)
    email_service.set_email_credentials(configuration.gmail_username,
                                        configuration.gmail_password)


def _make_user_bookings(users, days_in_advance):
    """ Create bookings for each user in `users`.
    :param users: list of Users to create bookings for
    :param days_in_advance: how far in advance to book
    :return: list of Booking instances containing all booked events
    """
    date_to_book = date.today() + timedelta(days=days_in_advance)
    bookings = []
    for user in users:
        bookings.append(user.create_booking(date_to_book))
    return bookings


def _send_user_reports(users, days_in_advance):
    """ Send reports to each user in `users`.
    :param users: list of User instances to send reports to
    :param days_in_advance: how many days in advance the reports should be for
    """
    date_for_report = date.today() + timedelta(days=days_in_advance)
    for user in users:
        user.email_report(date_for_report)


if __name__ == '__main__':
    main()
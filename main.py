from service import booking_service, raven_service
from datetime import date, timedelta
from configuration import Configuration
import sys


def main():
    configuration_file_path = sys.argv[1]
    configuration = Configuration(configuration_file_path)
    raven_service.set_default_credentials(configuration.default_crsid,
                                          configuration.default_password)
    _make_user_bookings(configuration.users, 2)


def _make_user_bookings(users, days_in_advance):
    """ Create bookings for each user in `users`.
    :param users: list of Users to create bookings for
    :param days_in_advance: how far in advance to book
    :return: list of Booking instances containing all booked events
    """
    date_to_book = date.today() + timedelta(days=days_in_advance)
    bookings = []
    for user in users:
        bookings += user.create_bookings(date_to_book)
    return bookings


if __name__ == '__main__':
    main()
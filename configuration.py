import json
from error import ConfigurationError
from model.user import User
from service import booking_service


class Configuration:
    """ A Configuration instance represents a system configuration. """

    def __init__(self, configuration_file_path):
        """ Construct a new Configuration, using the configuration within
        `configuration_file_path`.
        :param configuration_file_path: path to configuration file. See
            `configuration.example` for an example configuration
        :raises: ConfigurationError if the configuration file can't be loaded,
            or is not in the correct format
        """
        try:
            with open(configuration_file_path, 'r') as configuration_file:
                json_string = configuration_file.read().replace('\n', '')
            self._json_data = json.loads(json_string)
            self._default_crsid = self._json_data['default_crsid']
            self._default_password = self._json_data['default_password']
            self._gmail_username = self._json_data['gmail_username']
            self._gmail_password = self._json_data['gmail_password']
            self._users = None
        except IOError:
            raise ConfigurationError('Cannot load configuration file')
        except KeyError:
            raise ConfigurationError('Incorrect configuration file format')

    def _handle_booking_preferences_dict(self, booking_preferences_dict):
        """ Converts a standard textual representation of booking preferences
        to a weekday_index->events list.
        :param booking_preferences_dict: dictionary, mapping three-letter day
            codes (eg. 'mon', 'tue', ...) to a string describing the event the
            user wishes to book in to
        :return: list, indexed by day index (0 for Sunday, 1 for Monday, ...)
            where the elements are lists of Event instances that match the
            user's booking preferences
        """
        day_strings = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
        available_events = booking_service.get_available_events()

        booking_preferences = [[] for _ in range(7)]
        for user_day_string in booking_preferences_dict:
            if user_day_string.lower() in day_strings:
                day_index = day_strings.index(user_day_string.lower())
                user_event_string = booking_preferences_dict[user_day_string]

                def predicate(event):
                    return user_event_string.lower() in event.name.lower()
                matching_events = filter(predicate, available_events)
                booking_preferences[day_index] = matching_events
        return booking_preferences

    @property
    def default_crsid(self):
        return self._default_crsid

    @property
    def default_password(self):
        return self._default_password

    @property
    def gmail_username(self):
        return self._gmail_username

    @property
    def gmail_password(self):
        return self._gmail_password

    @property
    def users(self):
        """ Get the list of users for this system configuration
        :return: list of User instances
        :raises: ConfigurationError if the supplied configuration file isn't
            in the correct format
        """
        if self._users is not None:
            return self._users
        try:
            self._users = []
            for user_data in self._json_data['users']:
                crsid = user_data['crsid']
                password = user_data['crsid']
                friends = user_data['friends']
                booking_preferences_dict = user_data['events']
                booking_preferences = self._handle_booking_preferences_dict(
                    booking_preferences_dict)
                self._users.append(User(crsid, password, friends,
                                        booking_preferences))
            return self._users
        except KeyError:
            raise ConfigurationError('Incorrect configuration file format')
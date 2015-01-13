import json
from model.user import User
from error import ConfigurationError
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
            codes (eg. 'mon', 'tue', ...) to a list of strings describing
            events (eg. 'first', 'formal'), or a single string of this kind.
        :return: list, indexed by day index (0 for Sunday, 1 for Monday, ...)
            where the elements are lists of Event instances that the user
            wishes to book in to on that day
        """
        day_strings = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
        available_events = booking_service.get_available_events()

        booking_preferences = [[] for _ in range(7)]
        for user_day_string in booking_preferences_dict:
            if user_day_string.lower() in day_strings:
                day_index = day_strings.index(user_day_string.lower())
                user_event_strings = booking_preferences_dict[user_day_string]
                if type(user_event_strings) is unicode:
                    # We want to deal with a list of events.
                    if len(user_event_strings) == 0:
                        user_event_strings = []
                    else:
                        user_event_strings = [user_event_strings]
                events = []
                for user_event_string in user_event_strings:
                    def predicate(event):
                        return user_event_string.lower() in event.name.lower()
                    matching_events = filter(predicate, available_events)
                    if len(matching_events) > 0:
                        events.append(matching_events[0])
                booking_preferences[day_index] = events
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
                booking_preferences_dict = user_data['events']
                booking_preferences = self._handle_booking_preferences_dict(
                    booking_preferences_dict)
                self._users.append(User(crsid, password, booking_preferences))
            return self._users
        except KeyError:
            raise ConfigurationError('Incorrect configuration file format')
class Event:
    """ An Event represents a (possibly bookable) event that exists within the
    booking system.
    """

    def __init__(self, code, name):
        """ Construct a new Event instance.
        :param code: event code, used to identify this event within the
            booking system
        :param name: human-readable name for this event
        """
        self._code = code
        self._name = name

    @property
    def code(self):
        return self._code

    @property
    def name(self):
        return self._name

    def __str__(self):
        """
        :return: String representation of this event, in the format
            '<name> [<code>]'
        """
        return '%s [%d]' % (self.name, self.code)
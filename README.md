# CaiusHallHelper
Program to automate certain aspects of Caius hall, such as booking into events and receiving booking/menu email notifications.

# Requirements
Written in Python 2.
Requires Beautiful Soup (`pip install beautifulsoup4`) and Mechanize (`pip install mechanize`).

# Usage
`python main.py <configuration_file>`. `configuration.example` is an example configuration file, showing the information that should be included.

The program books you into events 3 days in advance, and sends email notifications for the day itself.

"""
Useful wrapper functions to access ConfigParser structures.
"""
from ConfigParser import NoSectionError, NoOptionError

def getboolean_default(config, section, option, default_value):
    """
	Return the given section.variable, or return the default if no specific
	value is set.
    """
    try:
        value = config.getboolean(section, option)
    except (NoSectionError, NoOptionError):
        value = default_value
    return value

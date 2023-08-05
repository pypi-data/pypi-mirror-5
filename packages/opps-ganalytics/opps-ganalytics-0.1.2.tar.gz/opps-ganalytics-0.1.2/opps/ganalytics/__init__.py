import pkg_resources


pkg_resources.declare_namespace(__name__)

VERSION = (0, 1, 2)

__version__ = ".".join(map(str, VERSION))
__status__ = "Development"
__description__ = u"Google Analytics for Opps CMS"
__author__ = u"Thiago Avelino"
__credits__ = []
__email__ = u"thiagoavelinoster@gmail.com"
__copyright__ = u"Copyright 2013, YACOWS"

import logging

from wikidp import template_filters

from . import (
    api,
    forms,
    pages,
    search,
)

logging.debug("Importing {}".format(template_filters.__name__))
logging.debug("Importing Routes".format(template_filters.__name__))

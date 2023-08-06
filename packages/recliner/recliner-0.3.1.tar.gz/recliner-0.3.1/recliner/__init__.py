from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from . import __about__
from .renderer import render, clean, htmlize


__all__ = ["render", "clean", "htmlize"] + __about__.__all__


# - Meta Information -
# This is pretty ugly
for attr in __about__.__all__:
    if hasattr(__about__, attr):
        globals()[attr] = getattr(__about__, attr)
# - End Meta Information -

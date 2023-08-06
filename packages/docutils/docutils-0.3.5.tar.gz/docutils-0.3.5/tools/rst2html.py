#!/usr/bin/env python

# Author: David Goodger
# Contact: goodger@python.org
# Revision: $Revision: 1.3 $
# Date: $Date: 2004/06/27 03:32:25 $
# Copyright: This module has been placed in the public domain.

"""
A minimal front end to the Docutils Publisher, producing HTML.
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description


description = ('Generates (X)HTML documents from standalone reStructuredText '
               'sources.  ' + default_description)

publish_cmdline(writer_name='html', description=description)

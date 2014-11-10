#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

config = {
    'command': re.compile(r'[\w@]'),
    'ignored_env': [
        'blockquote',
        'annotation'
    ]
}

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""notmm.controllers.SessionController API: A lightweight storage backend.

Copyright (c) 2007-2013 Etienne Robillard
All rights reserved.

<LICENSE=ISC>
"""
from notmm.controllers.wsgi import WSGIController
__all__ = ['SessionController']

class SessionController(WSGIController):
    
    def __init__(self, *args, **kwargs):
        """SessionController init method."""

        super(SessionController, self).__init__(*args, **kwargs)

    def getsessionid(self):
        return getattr(self, '_sid')
    
    @property
    def setsessionid(self):
        
        self._sid = getattr(self.settings, 'SECRET_ID', '123456789')
        return hash(self.getsessionid())


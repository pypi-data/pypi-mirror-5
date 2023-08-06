#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# For documentation and usage see
# http://gthc.org/NotAMonolithicMashup/I18NController

from .i18n import I18NController
import pubsub

__all__ = ['PubSubController']

class PubSubController(I18NController):
    wsgi_response_handlers = ('handle404', 'handle500')
    wsgi_response_enable_epoll = True

    def __new__(cls, *args, **kwargs):
        classobj = class.__new__(*args, **kwargs)
        classobj.sethandlers(classobj.wsgi_response_handlers)
        return classobj

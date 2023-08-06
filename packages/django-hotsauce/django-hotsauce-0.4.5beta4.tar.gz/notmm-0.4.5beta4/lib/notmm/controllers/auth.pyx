#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <LICENSE=ISC>
#
"""
Authentication and Authorization API version 0.4.5.

This is a thin wrapper on top of LibAuthKit to allow easy
integration with Django-based apps.
"""

#import logging
#log = logging.getLogger('notmm.controllers.wsgi')


try:
    #from authkit.authenticate import AuthTKTMiddleware as auth_app
    #from authkit.authenticate import middleware as auth_app
    from authkit.authorize import NotAuthenticatedError
    from authkit.authenticate.cookie import CookieUserSetter
except ImportError:
    raise ImportError("Authkit extension not installed or missing!")


from .session import SessionController

__all__ = ['AuthCookieController']

class AuthCookieController(SessionController):
    """
    Cookie-based authentication SessionController to delegate authorization 
    to a custom authorization backends (authkit.authorize).
    
    Features:
     * Experimental signed cookies (in module ``authkit.authenticate.auth_tkt``)
     * Session cookies (experimental)
     * etc etc..
    """
    # By default use signed cookies (Paste/Authkit implementation)
    # auth_middlewares = (AuthTKTMiddleware,)
    
    # set this to true to handle exceptions with Pastelib
    authkit_handle_exceptions = False


    def __init__(self, wsgi_app, auth_conf, **kwargs):
        # initialize SessionController middleware
        super(AuthCookieController, self).__init__(wsgi_app, **kwargs)

        self.auth_middleware = CookieUserSetter(wsgi_app,
            'd34db33fs41t',
            #auth_conf,
            #handle_exceptions=auth_conf.get('authkit.handle_exceptions', self.authkit_handle_exceptions),
            #valid=self.authenticate,
            #enforce=self.auth_conf['enforce']
            )
        
        setattr(self, 'auth_conf', auth_conf)



    def __call__(self, environ, start_response):

        self.init_request(self.environ)

        try:
            return self.application(self.environ, start_response)
        except NotAuthenticatedError:
            return self.handle403(self.request)

    def application(self, environ, start_response):
        # apply the response middleware wrapper to
        # the WSGI stack and return a callable obj

        return self.auth_middleware(environ, start_response)


    def authenticate(self, username, password):
        """
        Authenticate with the provided ``username`` and ``password``.

        Developers are expected to override this method in custom
        authentication subclasses.
        """

        if username == password:
            return username
        else:
            return None

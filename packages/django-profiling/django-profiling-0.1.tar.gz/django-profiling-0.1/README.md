django-profiling
================

Django Profiling Middleware with Admin integration.

Usage
=====

Install into your Django Python environment using your favorite tool.
Add `dprofiling` to your list of installed Django applications. Add 
`dprofiling.middleware.ProfileRequestMiddleware` to the top of you
middleware list. You can place it lower in the stack of middleware if
you do not want to profile your middleware in addition to the view.


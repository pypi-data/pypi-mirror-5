rebecca.login
===========================

.. image:: https://travis-ci.org/rebeccaframework/rebecca.login.png
   :target: https://travis-ci.org/rebeccaframework/rebecca.login

INSTALL
------------------------

::

  $ pip install rebecca.login


USAGE
----------------------------

``rebecca.login`` provides ``login`` and ``logout`` functions.
``login`` requires ``rebecca.repository.interfaces.IRepository`` named ``users``.

``login`` returns authenticated headers.

example::

    def login_success(self, values):
        user_name = values['user_name']
        password = values['password']
        authenticated = login(self.request, user_name, password)
        if not authenticated:
            return
        headers = security.remember(self.request, authenticated)
        response = HTTPFound(self.request.route_url('top'))
        response.headerlist.extend(headers)
        return response

Changes
=====================

0.1 (2013-11-16)
---------------------

- first release



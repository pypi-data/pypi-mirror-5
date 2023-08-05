****************
ZC WSGI Sessions
****************

This is an implementation of persistent sessions as a WSGI middleware
using `zope.session` as an underlying mechanism.

To use it:

1. Add `zc.wsgisessions` to `install_requires` list in `setup.py` of
   your application (e.g., `myapp`)

2. Add the following to `myapp.ini`::

    [filter:sessions]
    use = egg:zc.wsgisessions

   You can add to configuration::

    secure = true

   or::

    http-only = off

   Valid words are: `true`, `false`, `on`, `off`, `yes`, `no`, 1, and 0.

   You can also specify a database name for session storage::

    db-name = appdb

3. Add `sessions` to the pipeline *after* database middleware, but
   *before* the application.

4. Add to a function that is listed as `initializer` for the database
   middleware::

    zc.wsgisessions.sessions.initialize_database(database)

   You can also pass keyword arguments for: `db_name`, `namespace`,
   `secret`, `timeout`, and `resolution`.

5. Add to a function that is listed as `bobo.configure` (initializer of
   your WSGI application)::

    zope.component.provideAdapter(zc.wsgisessions.sessions.get_session)

6. You can use some helpers in your authentication code::

    PKG_KEY = __name__  # e.g., myapp.auth

    def get_user(request):
        return zc.wsgisessions.sessions.get(request, PKG_KEY, 'user')

    def save_user(request, user):
        zc.wsgisession.sessions.store(request, PKG_KEY, 'user', user)

    def forget_user(request):
        return zc.wsgisessions.sessions.remove(request, PKG_KEY, 'user')

7. When running `Selenium` tests, `HttpOnly` cookies cannot be used.
   Set the option ``'http-only': False`` in the `global_conf` dictionary
   of your testing application.


.. See ``src/zc/wsgisessions/sessions.txt`` for details.

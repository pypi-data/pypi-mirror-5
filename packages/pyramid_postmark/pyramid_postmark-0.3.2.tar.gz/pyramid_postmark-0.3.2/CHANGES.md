
# 0.3.2

Fix tests and add support for `paste.testing` WSGI environ flag. When True,
this flag shortcuts the `request.send_email` method to return a list of message
data, rather than actually calling mailer.send.

# 0.3.1

Bugfix.

# 0.3

Refactor slightly to use `config.add_request_method`.  Provide two new request hooks:

* `request.email_factory` to instantiate new PMMail instances
* `request.render_email` to instantiate new PMMail instances where the body is
  rendered using a template

# 0.2

Implement basic background sending.

# 0.1

Initial version.

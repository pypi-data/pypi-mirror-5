
## 0.9.2

0.9.1 was a brown bag: the sdist was missing the form.mako template.

## 0.9 / 0.9.1

Improved docs.

## 0.8.5

Added ``snip_text`` and ``snip_html`` functions to template namespace.

## 0.8.4

Added Redis ``queue.QueueProcessor``.

## 0.8.3

Added `fileupload` template def.

## 0.8.2

Override ``request.route_url`` to force urls to use a secure protocol when
force https is enabled.

## 0.8

Provide `nav` module to add `is_active` to the template namespace.

## 0.7

* hsts support to add force https
* tx module with `join_to_transaction` function
* `had_been_seen` and `session_id` request properties
* `generate_random_digest`, `get_stamp` and `datetime_to_float` utility functions

## 0.6

Remove the `.auth` module (having implemented 
[pyramid_simpleauth](http://github.com/thruflo/pyramid_simple_auth)).

Removed the `passlib` and `setuptools_git` dependencies.

## 0.5

Renamed `_csrf_token` request parameter to `_csrf` (a more widely used default).

## 0.4

Added `.auth` module with password `encrypt()` and `verify()` functions.  

(n.b.: This introduces a dependency on 
[passlib](http://pypi.python.org/pypi/passlib/), which atm requires a 
`python setup.py install` from source to work under Python 3).

## 0.3

Remove the ``BaseView`` class and the method selecting functionality, as it
just doesn't work with Pyramid's view configuration.

Re-factored the CSRF validation into a subscriber as a consequence.

## 0.2.1

Fixed the `.i18n.add_underscore_translation` subscriber.

## 0.2

Added i18n features.

## 0.1

Initial version.
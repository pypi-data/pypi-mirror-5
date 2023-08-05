milo
====

Library of useful Python code

This is being published primarily so that the author can "pip install" it
wherever fine virtualenvs can be found. However, anyone else is free to
read and use it. Pull requests are welcome and will be added if they 
fit in with the main goal of this project.

This library contains useful bits of code, mostly small functions, which I've
found myself rewriting or copying and pasting.

Current contents:

* a memoize function implemented in Redis
* a simple XML -> dictionary parser
* polite_get: get a URL, with auto-caching
* a simple get_logger that logs to a temp file, and stdout if interactive

Planned additions:

* easy command-line e-mail utility, with attachments

Dependencies:

* the `redis` module
* the `requests` package

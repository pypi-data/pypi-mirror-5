================
gargant.dispatch
================

Flexible dispatcher for WSGI application.

Basic usage
===========

Writing dispaching tree, and register wsgi apps to `case`::

    from wsgiref.simple_server import make_server
    from gargant.dispatch import Node, path_matching, make_wsgi_app

    from path.to.yours import wsgi_app


    tree = Node((path_matching(['']),),
                case=wsgi_app,
                name='first')

    app = make_wsgi_app(tree)

    httpd = make_server('', 8000, app)
    httpb.serve_forever()


Registered app (wsgi_app) will be called when the path is '/'.

Node
====
gargant.dispatch is not just for creating a WSGI application.
It can handle environ and return a value as you like.

You can apply anything to `case`::

    >>> tree = Node((path_matching(['']),),
    ...             case='dolls')
    >>>
    >>> node = tree({'PATH_INFO': '/'})
    >>> node.case  # 'dolls'


Hierarchy
---------

Node class can take argument 'children' like this::

    >>> tree = Node((path_matching(['']),),
    ...             case='dolls',
    ...             children=(
    ...                 Node((path_matching['fifth']),
    ...                      case='shinku'),
    ...             ))
    >>>
    >>> node = tree({'PATH_INFO': '/fifth'})
    >>> node.case  # 'shinku'

There is not any matched children, the parent will be matched::

    >>> node = tree({'PATH_INFO': '/'})
    >>> node.case  # 'dolls'

Matching
========
path_matching is just one of matching patterns,
you can use method_matching too::

    >>> tree = Node((path_matching(['']),
                     method_matching('get')),
    ...             case='dolls',
    ...             )
    >>>
    >>> node = tree({'PATH_INFO': '/',
    ...              'REQUEST_METHOD': 'GET'})
    >>> node.case  # 'dolls'

method patterns returns callables taking environ and return
some values.
All values returned from matchings can be handles as True.
The Node will be handles as 'matched'.

Returned values from matchings will be store in
node.matched as list of these.

URL args
--------

And using this behavior, path_matching can take args from URL::

    >>> tree = Node((path_matching(['']),),
    ...             case='doll_list',
    ...             children=(
    ...                 Node((path_matching(['{doll}']),),
    ...                       case='doll_detail',
    ...                 ),
    ...             ))
    >>>
    >>> node = tree({'PATH_INFO': '/first'})
    >>> node.case  # 'doll_detail'
    >>> node.matched[0]['doll']  # 'first'

Adapters
=========
Node can take keyword arg named `adapter_factory`.
It takes node.matched and return some callables you like::

    >>> tree = Node((path_matching(['']),),
    ...             case='dolls',
    ...             children=(
    ...                 Node((path_matching(['fifth']),),
    ...                       case='shinku',
    ...                       adapter_factory=lambda matched: lambda x: x + ' kawaii'
    ...                 ),
    ...             ),
    ...             adapter_factory=lambda matched: lambda x: x + ' is'
    ...             )
    >>>
    >>> node = tree({'PATH_INFO': '/fifth'})
    >>> node.case  # 'shinku'
    >>> doll = 'shinku'
    >>> root_to_leaf = reversed(list(node))  # [dolls node, shinku node]
    >>> for node in root_to_leaf:
    ...     doll = node.adapter(doll)
    ...
    >>> doll  # 'shinku is kawaii'

In this case, these adapter_factory will return simple functions,
but gargant.dispatch is assuming you make it to return Adapter classes.

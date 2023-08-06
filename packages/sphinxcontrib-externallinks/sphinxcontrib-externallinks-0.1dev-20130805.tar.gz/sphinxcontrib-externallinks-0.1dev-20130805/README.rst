sphinxcontrib.externallinks
===========================

Roles
-----

This module defines some roles.

`google` It takes a single, requiredargument, keywords for search::

    :google:`world heritage sites in japan`

`google-images` It takes a single, requiredargument, keywords for image search::

    :google-images:`world heritage sites in japan`

`google-maps-fromto` It takes a single, requiredargument, keywords for maps search::

    :google-maps-fromto:`from Mt.Fuji to Hiraizumi` by public transit
    :google-maps-fromto:`driving from Mt.Fuji to Hiraizumi` by car
    :google-maps-fromto:`walking from Mt.Fuji to Hiraizumi`

    :google-maps-fromto:`from Mt.Fuji to Hiraizumi <富士山,平泉町>` by public transit
    :google-maps-fromto:`driving from Mt.Fuji to Hiraizumi <富士山,平泉町,d>` by car
    :google-maps-fromto:`walking from Mt.Fuji to Hiraizumi <富士山,平泉町,w>`

`tenkipast` It takes a single, requiredargument, prefecture and date for the weather of the past in Japan(tenki.jp)::

    :tenkipast:`東京,2013/07/16`

Directives
----------

This module defines some directives.

`google-maps` It takes a single, requiredargument, keywords for maps search::

    .. google-maps: driving from Mt.Fuji to Hiraizumi
      :saddr: 富士山
      :daddr: 平泉町
      :dirflg: d

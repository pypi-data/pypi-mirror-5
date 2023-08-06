.. contents::


Installation
============

Install the distribution from source::

    $ python setup.py install

Or install with ``easy_install``::

    $ easy_install fnord.easycodec


Usage
=====

This package can be used to easily create and register codecs.

Use the decorator ``encoder`` to create an encode-function::

    >>> from fnord.easycodec import encoder
    >>> @encoder("my_codec")
    ... def my_encode(message):
    ...     ...

(``my_codec`` is the name of the codec.)

Use the decorator ``decoder`` to create a decode-function::

    >>> from fnord.easycodec import decoder
    >>> @decoder("my_codec")
    ... def my_decode(message):
    ...     ...

Use the factory ``CodecRegistration`` to create an object that can be
returned by a codec's search-function::

    >>> from fnord.easycodec import CodecRegistration, AUTO
    >>> registration = CodecRegistration(
    ...     "my_codec", my_encode, my_decode,
    ...     streamwriter=AUTO, streamreader=AUTO)

This factory takes the following parameters:

:``name``: The name of the codec.  Required.
:``encode``: The encode-function.  Required.
:``decode``: The decode-function.  Required.
:``incrementalencoder``: The incremental encoder.  Optional.
:``incrementaldecoder``: The incremental decoder.  Optional.
:``streamwriter``:  The stream-writer.  Optional.
:``streamreader``:  The stream-reader.  Optional.

If one of the optional parameters has the value ``AUTO`` assigned, an
appropriate object will be generated and used.

Use the factory ``CodecSearch`` to create a search-function for a codec.  The
parameters are the same as for ``CodecRegistration``::

    >>> from fnord.easycodec import CodecSearch
    >>> search = CodecSearch(
    ...     "my_codec", my_encode, my_decode,
    ...     streamwriter=AUTO, streamreader=AUTO)

This function can then be used to register the codec::

    >>> import codecs
    >>> codecs.register(search)

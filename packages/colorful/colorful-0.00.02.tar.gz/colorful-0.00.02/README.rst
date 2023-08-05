colorful
========

    python module to decorate text with ANSI colors and modifiers
    *Version: 0.00.01*

--------------

**Author:** Timo Furrer tuxtimo@gmail.com\  **Version:** 0.00.01
**License:** GPL (See ``LICENSE``)

What the fuck?
--------------

With this module you can decorate some text with colors. The methods
which gets invoked are dynamically generated.

For example:

.. code:: python

    from colorful import Colorful

    print( Colorful.bold_red_on_black( "Hello World!" ))
    print( Colorful.black_on_white( "Hello World!" ))
    print( Colorful.underline( "Hello World!" ))
    print( Colorful.bold_and_underline_green( "Hello World!" ))
    print( Colorful.bold_and_underline_green_on_red( "Hello World!" ))
    print( Colorful.bold_and_underline_and_strikethrough_green_on_red( "Hello World!" ))
    print( Colorful.strikethrough( "Hello World!" ))

    # Or direct print:
    Colorful.out.bold_red_on_black( "Hello World" )
    Colorful.out.underline( "Hello World" )
    Colorful.out.bold_and_underline_green_on_white( "Hello World!" )

Available modifiers and colors
------------------------------

Modifiers:
~~~~~~~~~~

-> reset -> bold -> italic -> underline -> blink -> inverse ->
strikethrough

Forecolors:
~~~~~~~~~~~

-> black -> red -> green -> brown -> blue -> magenta -> cyan -> white ->
normal

Backcolors:
~~~~~~~~~~~

-> black -> red -> green -> yellow -> blue -> magenta -> cyan -> white
-> normal

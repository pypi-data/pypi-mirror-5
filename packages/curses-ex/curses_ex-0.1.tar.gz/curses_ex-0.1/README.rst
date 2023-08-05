curses_ex
==================================

curses_ex is Python extension module to provides some funtions not supported by standard `curses <http://docs.python.org/3/library/curses.html>`_ package.

define_key(definition=None, keycode=None)
-------------------------------------------------

It permits an application to define keycodes with their corresponding control bytes, so that the ncurses library will interpret them just as it would the predefined codes in the terminfo database.

If the given definition is None, any existing definition for the keycode is removed. Similarly, if the given keycode is None, any existing string for the given definition is removed.

key_defined(definition)
-----------------------------------------------

It permits an application to determine if a string is currently bound to any keycode.

If the string is bound to a keycode, its value (greater than zero) is returned. If no keycode is bound, zero is returned. If the string conflicts with longer strings which are bound to keys, -1 is returned. 


License
-------------------------------------

Copyright (c) 2013 Atsuo Ishimoto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


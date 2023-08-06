Changelog
=========

0.0.5 (2013-09-16)
------------------

New
~~~

- Color names are case insensitive. [Chris Priest]

  The color-name structure have their names capitalized. And color names
  that are made of only one word will be displayed lowercased.

Fix
~~~

- Now using W3C color recommandation. [Chris Priest]

  Was using X11 color scheme before, which is slightly different from
  W3C web color specifications.

- Inconsistency in licence information (removed GPL mention). (fixes #8)
  [Valentin Lab]

- Removed ``gitchangelog`` from ``setup.py`` require list. (fixes #9)
  [Valentin Lab]

0.0.4 (2013-06-21)
------------------

New
~~~

- Added ``make_color_factory`` to customize some common color
  attributes. [Valentin Lab]

- Pick color to identify any python object (fixes #6) [Jonathan Ballet]

- Equality support between colors, customizable if needed. (fixes #3)
  [Valentin Lab]

0.0.3 (2013-06-19)
------------------

New
~~~

- Colour is now compatible with python3. [Ryan Leckey]



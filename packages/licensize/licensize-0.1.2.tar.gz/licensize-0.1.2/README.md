
Licensize is a super simple app that adds a LICENSE file to your current
directory.

Installation
-------

From PyPi:

    pip install licensize

Manually:

    python setup.py install


Usage
-------

Just do...

    licensize

...to license the current directory as GPL 3.0 using your git or mercurial
config name in the copyright notice. Or...

    licensize -a 'Hacker Corp.' -l mit -n COPYING

...to save the MIT license licensed to 'Hacker Corp.' to a COPYING file in the
current directory.

License name list is searched for close matches with a preference on newer
more common licenses, so "bsd" will match "BSD 3 Clause", and "bsd2" will
match "BSD 2 Clause".


Purpose
---------

It's a great script to speed up creating a new repo for a little FOSS licensed
library or something, like if you want to quickly spin off a rails / Django
app, or jQuery plugin, as a properly licensed GPL or MIT licensed FOSS software
package.  Hopefully will help combat "license laziness" which plagues
github/bitbucket presently with so many un-licensed projects.

Contributing
---------

Fork requests are welcome of course :)


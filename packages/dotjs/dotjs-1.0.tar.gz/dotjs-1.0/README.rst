dotjs
=====

dotjs is a Google Chrome extension that executes JavaScript files in
``~/.js`` based on their filename.

If you navigate to ``http://www.google.com/``, dotjs will execute
``~/.js/google.com.js``.

This makes it super easy to spruce up your favorite pages using
JavaScript.

On subdomains such as ``http://gist.github.com`` dotjs will try to load
``~/.js/gist.github.com.js`` as well as ``~/.js/github.com.js`` and
``~/.js/com.js``.

Bonus: files in ``~/.js`` have jQuery 1.9 loaded, regardless of whether
the site you're hacking uses jQuery.

Double bonus: ``~/.js/default.js`` is loaded on every request, meaning
you can stick plugins or helper functions in it.

GreaseMonkey user scripts are great, but you need to publish them
somewhere and re-publish after making modifications. With dotjs, just
add or edit files in ``~/.js``.

Example
-------

::

    $ cat ~/.js/github.com.js
    // swap github logo with trollface
    $('a[class^=header-logo-]').html(
    $('<img>')
        .attr('src', '//bit.ly/ghD24e')
        .css({'width': 'auto', 'height': '22px'})
    );

.. figure:: http://puu.sh/1Kjvw
   :alt:

How It Works
------------

Chrome extensions can't access the local filesystem, so dotjs runs a
tiny web server on port 3131 that serves files out of ~/.js.

The dotjs Chrome extension then makes ajax requests to
http://localhost:3131/convore.com.js any time you hit a page on
convore.com, for example, and executes the returned JavaScript.

Requires
--------

-  Python >= 2.6
-  Google Chrome

Install it
----------

::

    git clone http://github.com/hackedd/python-dotjs
    cd python-dotjs
    python setup.py install

Now open https://localhost:3131 in Chrome and follow these steps:

OS X:
~~~~~

-  Click the "X" Padlock icon in the address bar
-  Click "Certificate Information"
-  Drag the large cert icon to your desktop
-  Open it with Keychain
-  Configure its **Trust** section as shown: http://cl.ly/Pdny

Windows:
~~~~~~~~

-  Click the "X" Padlock icon in the address bar
-  Click "Certificate Information"
-  On the "Details" tab, click "Copy to File..."
-  Export the certificate as a ".cer" file
-  Right-click the exported ".cer" file, click "Install Certificate"
-  Complete the Wizard to import the certificate to the Windows
   Certificate store. Make sure to select ``Trusted Root Certification
   Authorities`` as the destination store when asked.

Ubuntu:
~~~~~~~

-  Use ``certutil`` to import the certificate to your NSS database::

    echo | openssl s_client -connect localhost:3131 2>&1 | \
        sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > /tmp/dotjs.crt
    certutil -d sql:$HOME/.pki/nssdb -A -t "P,," \
        -n localhost-dotjs -i /tmp/dotjs.crt

Finally install the Google Chrome extension:

http://bit.ly/dotjs

Credits
-------

-  Original version: https://github.com/defunkt/dotjs
-  Icon: http://raphaeljs.com/icons/
-  jQuery: http://jquery.com/
-  Ryan Tomayko for:

    "I almost wish you could just stick JavaScript in ~/.js. Do you know
    what I'm saying?"

Other Browsers
--------------

-  `Firefox Add-on`_
-  `Safari Extension`_
-  `Fluid UserScript`_

.. _Firefox Add-on: https://github.com/rlr/dotjs-addon
.. _Safari Extension: https://github.com/wfarr/dotjs.safariextension
.. _Fluid UserScript: https://github.com/sj26/dotjs-fluid

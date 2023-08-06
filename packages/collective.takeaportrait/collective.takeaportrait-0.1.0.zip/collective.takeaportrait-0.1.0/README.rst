This product use super-modern browser feature for **accessing the user's webcam** (if any) to directly save a
new portrait photo inside Plone personal preferences.

.. contents::

How it works
============

Just add the product to your buildout and activate the *collective.takeaportrait* add-on.

After that you will probably see a new button inside your "*Personal Information*" labeled "*Take a photo*". 
If you don't see any new button your browser will probably not support Media Capture API.

.. image:: http://keul.it/images/plone/collective.takeaportrait/collective.takeaportrait-0.1.0-01.png
   :alt: alternate text
   :align: center

.. image:: http://keul.it/images/plone/collective.takeaportrait/collective.takeaportrait-0.1.0-02.png
   :alt: alternate text
   :align: left

.. image:: http://keul.it/images/plone/collective.takeaportrait/collective.takeaportrait-0.1.0-03.png
   :alt: alternate text
   :align: right

When pressing the button the browser will ask you the permission to access the Webcam and you must accept
to continue. The security request format is vendor specific.

When confirmed you will see the new portrait overlay, where the webcam is activated and the output stream
is directly on your browser.

.. image:: http://keul.it/images/plone/collective.takeaportrait/collective.takeaportrait-0.1.0-04.jpg
   :alt: alternate text
   :align: center

You have two possible actions: close the window or take a photo. In the latter case a delay counter will be
displayed on the left (you can raise or lower the delay using the range control, from 0 to 10 seconds).

.. image:: http://keul.it/images/plone/collective.takeaportrait/collective.takeaportrait-0.1.0-05.jpg
   :alt: alternate text
   :align: center

Note: only the image part inside the highlight yellow section will be used as a new portrait.

After every shot taken, you can look at a preview of the image, and repeat the operation until you get a nice
portrait.

.. image:: http://keul.it/images/plone/collective.takeaportrait/collective.takeaportrait-0.1.0-07.jpg
   :alt: alternate text
   :align: center

Finally, you can save the new portrait in the user's preferences. The image in the form will be immediately
updated from the server.

.. image:: http://keul.it/images/plone/collective.takeaportrait/collective.takeaportrait-0.1.0-08.png
   :alt: alternate text
   :align: center

Plone integration
=================

As customizing the user preference form is something I don't like very much, this product is adding new features
only using pure JavaScript.

Tested on Plone 4.3.

Browsers support
================

The user's browser must support `HTML Media Capture API`__ so only recent and cool browser can be used:

* Firefox: tested with Firefox 25
* Chrome: tested with Chrome 30 (a little slow, but works)
* Opera: tested with Opera Next, version 18
* Safari: no support (c'mon Apple...)
* Internet Explorer: support is expected for Internet Explorer 31 [1]_
* Mobile: no test done  apart Safari on iOS (and it's not working)

To know if your browser is supported, see the `Can I Use`__ Web site.

__ http://www.w3.org/TR/html-media-capture/
__ http://caniuse.com/stream

.. [1] Microsoft said that probably the Media Capture support will be delayed to Internet Explorer 36 in case
       Patent War VI against Kilrathi race on Tau Ceti will not over on time.

=============================
Static HTML gallery generator
=============================

Convert pictures and videos from a directory to another directory
where the pictures are recompressed and resized and the videos are
converted to WebM & MP4, then generate the HTML pages.

Browsing is done using `Colorbox`_, a jQuery-based Lightbox clone.

Videos are displayed using `Video.js`_.

.. _Colorbox: http://www.jacklmoore.com/colorbox/
.. _Video.js: http://www.videojs.com/


TODO:

- modify colorbox to insert a link to the original image (there's something
  like this currently but it's a hack)
- parralelize conversions using a thread pool (when work is done by forking
  commands, not when using PIL)

Changelog
=========

0.2 (2013-05-08)
----------------

- slider items can link to other portal content using related items
  (see ``imageslider_teaser_link_related`` in the README)
  
- pass image object to page-template too, so customized versions can use
  plone.app.imaging scales if the want to.

- only show navigation if there are more than 1 images

- bugfix: images overlapped due to bug in circular implementation.
  wrapping initialization with a timeout fixes the problem

- nicer layout for image captions using rgb() css transparency instead
  of opacity (similar to newsitem_view)
  

0.1.1 (2012-05-30)
------------------

- fix autoscroll configuration (a typo in `interval`
  prevented the settings to take effect)

0.1 (2012-05-29)
----------------

- initial release [fRiSi]

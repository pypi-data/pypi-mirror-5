Installation
============

This documentation assumes that your installation of Plone/Zope is
based on zc.buildout.


-  edit your *buildout.cfg*
-  add ``zopyx.authoring`` to the ``zcml`` option of
   your buildout.cfg::

    eggs = ...
        zopyx.authoring
    

-  re-run::
 
      bin/buildout

-  restart Zope/Plone

-  now either create a new Plone 4 site through the ZMI and select the ``Authoring Environment``
   profile from the list of available extension profiles or 

    .. image:: images/ae_install_zmi.png

  
   visit the add-ons control panel within the Plone UI and add
   ``Produce & Publish Authoring Environment`` to the list of installed add-ons

    .. image:: images/ae_install_plone.png


 .. note:: The Produce & Publish Authoring Environment requires an installation
     of ``pp.server`` Produce & Publish server. An installation of the
     older``zopyx.smartprintng.server`` Produce & Publish server will not work.

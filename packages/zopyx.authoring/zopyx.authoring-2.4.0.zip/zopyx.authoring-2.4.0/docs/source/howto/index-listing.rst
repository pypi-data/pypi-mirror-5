How to create an index list with index terms
============================================

Produce & Publish provides a simple build-in mechanism for generating a list
of index terms with their occurrence (page-numbers).

Prequisites
-----------

All index terms must be marked using::

    <span class="index-term">some index term</span>

This can either be accomplished by generating the related markup through the
content-type specific browser views/templates that are registered as
``@@asHTML`` view (Produce & Publish Plone Client Connector) or you highlight a
term inside TinyMCE and apply the style ``Index term`` from the styles dropdown
menu (Produce & Publish Authoring Environment).

Generating an index through the Plone Client Connector
------------------------------------------------------

The standard ``@@asPlainPDF`` view of the Plone Client Connector will
automatically create an index listing at the end of the document. The
underlaying transformation ``addIndexList`` is called automatically (see
``pdf.py`` file within the client connector sources)

Generating an index through the Authoring Environment
-----------------------------------------------------

Inside the Authoring Environment have the option to create individual listings
including an index listing by checking the related checkbox from the ``PDF``
tab of your conversions page.

Custom location of the indexes listing inside your template
-----------------------------------------------------------

By default the index listing will be added to the end of the document. However you can
control the place through a custom PDF rendering template (e.g. inside your own 
resources directory). You may place the following markup e.g. in front or after the body
text::

    <div id="indexes-list">
        index listing will be inserted here
    </div>


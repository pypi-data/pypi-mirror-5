Managing and organizing your content
====================================

Your content can be organized as hierarchial set of folders, pages and images.
The folder structure determines the later structure of your document.                                                          

Inside the root authoring content folder you can add the following content
types.

AuthoringContentFolder
----------------------

A standard Plone folder holding other folders and pages

AuthoringContentImage
---------------------

A standard image content type holding one image. The authoring environment
keeps the original size/resolution of the image. The original and full
resolution of the images will always be used for generating PDF documents.
The authoring environment does support generating a PDF document with a
reduced size. However this conversion happens as a dedicated post-processing step 
after generating the PDF with the full-size image. The Image type provides 
several additional settings that are related to the PDF conversion.

.. image:: images/add-image.png

Scale for PDF production
++++++++++++++++++++++++

This parameters determines the horizontal width in percent of the image inside
the generated PDF document. Adjust this parameter in case an image would use
too much space or cause an unwanted page break.

Exclude from image enumeration
++++++++++++++++++++++++++++++

By default, all images will be enumerated. This checkbox can be used to exclude
an image from the enumeration.

Create image link to full scale in HTML view
++++++++++++++++++++++++++++++++++++++++++++

The authoring environment will not generate a link to the full view of an image
if you decide to generate a HTML version of your content. However by checking
the checkbox you can enable this option.

Display image inline
++++++++++++++++++++

By default, images are displayed as a block without text floating around them. In cases
when you need to include an image as part of a paragraph (e.g. icon images used
inside a legend of a table or an image) you may choose to display this
particular image inline. Inline images will not be enumerated.

Caption position
++++++++++++++++

The authoring environment will generated image captions for each image (if it
is not inlined). The image caption is taken from the ``description`` metadata
of the image. So make sure that the description metadata is maintained properly
- otherwise you may encounter a warning in the generated documents. The
position of the image caption can be below or above the image.

AuthoringContentAggregator
--------------------------

A content aggregator can be used to reference existing content inside other
content folders. The basic purpose is to re-use existing content in order to
avoid redundancies. 

.. image:: images/add-aggregator.png

By adding an aggregator you have the option to reference either another content
folder or an existing content page. The aggregator acts as a transparent proxy
for the referenced object.  The conversion engine of Produce & Publish will
replace an aggregator during the conversion with the content of the referenced
content page or content folder.

The detail view of a content aggregator object will show additional information
about the referenced object.

.. image:: images/view-aggregator.png


LinkTool
--------

The Authoring Environment allows you to create links to other content pieces
without creating the _traditional_ HTML anchors yourself. The Authoring
Environment will insert automatically internal **ID** attributes for the
following elements in order to make them directly linkable:

* tables
* headings (H1, H2, H3, ...)
* list items
* images

The Authoring Environment provides a new TinyMCE plugin: the **LinkTool**.
You can use the **LinkTool** selecting a text within TinyMCE and clicking on the 
**LinkTool** icon of the TinyMCE toolbar.

.. image:: images/linktool_start.png

The **LinkTool** displays all linkable content items grouped by documents.

Linking to headings
+++++++++++++++++++

.. image:: images/linktool_headings.png

Linking to tables
+++++++++++++++++

Tables are represented by their caption or summary. So ensure that your
table contains a proper caption or summary.

.. image:: images/linktool_tables.png

Linking to images
+++++++++++++++++

All linkable images are represented by their thumbnail images.

.. image:: images/linktool_images.png

Linking to list items
+++++++++++++++++++++

You can create links to arbitrary list items ((un)ordered list and definition
lists are supported). The typical usecase is e.g. a literature list represented
as a list. Inside the content you are then able to reference those list item
entries.


.. image:: images/linktool_listitems.png

Working with tables
-------------------

Produce & Publish does not provide any extra functionality for editing tables
using the TinyMCE editor of Plone 4 or higher. It provides only two additional
CSS classes ``Grid + Landscape`` and ``No grid + Landscape``. The landscape
mode will render a table in the PDF output in landscape mode on a dedicated
page. This can be used for table with an excessive width.

Conversion control center 
=========================

The Conversion Control Center is where you manage all your work.

.. image:: images/cc_view.png

The links behind the **Contents folder** give you access to your configured contents folder.
The eye icon will give you view access to the content folder while the pencil icon will
open the first content object in edit mode.

.. image:: images/cc_content_folder.png

Inspectors
----------

The Conversion Control Center comes with several inspectors that allow you to
check several aspects of your authoring project for consistency.

Image inspector
+++++++++++++++

The image inspectors displays all referenced images (in thumbnail size)
together with all conversion related parameters. The most common problem are
images without a description. The description is used for the caption of an
image and therefore must be filled out. An image with a  missing description
will be marked with an exclamation mark.

.. image:: images/cc_inspector_image.png

Anchor inspector
++++++++++++++++

The anchor inspector shows all internal cross-references. Stale references will
be marked with an exclamation mark or a green check sign as shown in the
picture.

.. image:: images/cc_inspector_anchors.png

Document structure inspector
++++++++++++++++++++++++++++

The document structure inspector checks your document for logical errors. E.g.
a ``H1`` heading can not be followed by a ``H3`` heading.

.. image:: images/cc_inspector_document_structure.png

Links inspector
+++++++++++++++

For inspection completeness the Links inspector will list all links to external
pages including their link text.

.. image:: images/cc_inspector_links.png

Conversion workflow
-------------------

Every conversion output (PDF, EPUB etc.) will be stored in a dedicated
``Drafts`` folder that you can see at the bottom of the conversions center
view.

.. image:: images/drafts_published.png

All entries are sorted by creation date (newest first). By clicking on
conversion result you can either download the generated file or view them
within a browser (HTML + PDF conversion). Additional information about 
size, creation date and creator is provided.

If you are fine with conversion result then you can click on ``publish/rename``
and the conversion result will be moved into the configured
``Publications`` folder. The workflow state of all content will be automatically changed
to state ``published``.


Pasting content from Microsoft Office (Word) into Plone
========================================================

It seems to be a common approach to edit content within Word on Windows and
then to insert the content using copy & paste into Plone

The problem
------------

The content copied from Word contains a lot of additional and partly improper
HTML markup which may cause trouble in Plone - both from the visual and
functionality point of view. So in general it is **forbidden** to paste
Word content directly into the editor window of Plone.

The solution
------------

Click on the the ``Paste from Word`` icon inside the toolbar of the editor
and paste the Word content into the textarea inside the popup window and then
just click on ``Insert``. This will remove most of the Word markup crap
often causing problems.

.. image:: images/paste_from_word.png

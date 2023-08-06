Customizing S5 templates and styles (Authoring Environment)
===========================================================

There are two files relevant to the S5 conversion.  The rendering template is
defined in
``zopyx.authoring/zopyx/authoring/browser/s5_presentation_template.pt`` and
``zopyx.authoring/zopyx/authoring/skins/zopyx_authoring/pp-s5-pretty.css``. If
you need to customize your files then you have basically two options inside
your own policy/theme package:

- provide your own versions of the files through the overrides mechanism of
  ZCML for overriding the presentation template and your own skins directory
  for overriding the CSS file

or

- using ``z3c.jbot`` for overriding both the presentation template and the
  stylesheet through one customization mechanism (recommended)

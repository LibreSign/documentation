=============================
LibreSign manuals style guide
=============================

*This is a work in progress*

See the `Documentation README <https://github.com/LibreSign/documentation/blob/main/README.rst>`_ for information on setting up your documentation build environment

See `reStructuredText Primer <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_ for a complete 
Sphinx/RST markup reference.

This is the official style guide for the LibreSign Administration and User 
manuals. Please follow these conventions for consistency, and easier 
proofreading and copyediting.

When you are writing your text, make it as literal and specific as possible. Put 
yourself in the place of the person who is using LibreSign and looking for 
instructions on performing a task. Don't make them guess, but spell 
out every step in order, and tell exactly what buttons to click or what form 
fields to fill out. Give complete information; for example, when making an OCC
configuration change, specify the exact command to run, with the exact
parameters, and the exact user to run it as. When you are describing 
features of a GUI administration form use the exact literal names of buttons, 
form fields, and menus in English. Specify if menus are dropdown, right-click, 
left-click, or mouseover.

Page filenames
--------------

Use lowercase filenames with underscores, for example file_name_config.rst.

Page titles and headings
------------------------

There are many ways to markup headings and subheadings. This is the official 
LibreSign way. Use sentence case. Three levels is enough; if you find that you want more, 
then re-think the organization of your text::

 ==============
 Page title, h1
 ==============

 Subhead, h2
 -----------

 Subhead, h3
 ^^^^^^^^^^^

This is how they render:

==============
Page title, h1
==============

Subhead, h2
-----------

Subhead, h3
^^^^^^^^^^^

Labels and code
---------------

Elements in a GUI configuration form are in bold, and should be described as 
literally as possible, so that your description matches what your reader sees 
on the screen. For example, on the User listing page describe the various 
elements like these examples::

 **Username** field
 **Password** field
 **Groups** dropdown menu
 **Create** button
 **Full Name** field
 **Quota** dropdown menu
 
This is how they render:
 
**Username** field

**Password** field

**Groups** dropdown menu

**Create** button

**Full Name** field

**Quota** dropdown menu

.. figure:: users-config.png
   :alt: User listings and administration page.
   
   *Figure 1: The file listing and administration page.*
   
Use double-backticks for inline code and command examples::
  
  ``sudo -E -u www-data php occ libresign:configure:check --help``
  ``libresign:uninstall --jsignpdf``
  
This is how they render:

``sudo -E -u www-data php occ libresign:configure:check --help``

``libresign:uninstall --jsignpdf``

When you are giving hyperlinks as examples, use double-backticks rather than 
creating a live hyperlink::

 ``https://example.coop``

Images
------

Use lowercase with hyphens for image names, for example image-name.png.

Images should be in .png format. Keep your screenshots focused on the items you 
are describing. When you need an image of something large like a configuration 
form on the LibreSign admin page, narrow your Web browser to fold the fields 
into a smaller space, because a long skinny graphic is not very readable. Think 
square.

Both images and figures must have brief and descriptive alt tags and all 
figures must have captions with figure numbers. Sphinx RST markup does not 
have a tag for figure numbers, so you must 
use the caption element. You may use simple numbering like "Figure 1, Figure 2", 
or add a caption. Captions must follow a blank line and be italicized, like this example::

  .. figure:: images/users-config.png
     :alt: User listings and administration page.
     
     *Figure 1: The file listing and administration page.*

Images must go into a sub-directory of the directory containing your manual 
page. Currently the manuals have both a single master images directory, and 
image directories local to each chapter. A single master images directory is 
difficult to maintain and inevitably becomes cluttered with obsolete images. Eventually
the single master directories will be gone.

Example URL
-----------

Use ``https://example.coop`` in your examples where you want to include an URL.

This style_guide was based on the `Nextcloud documentation <https://github.com/nextcloud/documentation/blob/master/style_guide.rst>`_.
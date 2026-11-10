=======================
LibreSign Documentation
=======================

The public manuals are published at https://docs.libresign.coop.
Documentation uses Sphinx and reStructuredText (RST).

Choose the correct version before editing
-----------------------------------------

Each LibreSign release has **one complete documentation branch**:

* ``main``: the next LibreSign version (development).
* ``stable15``: LibreSign 15.
* ``stable14``: LibreSign 14.
* ``stable13``: LibreSign 13.

Future releases use the same naming convention (``stable16``, etc.).
Unlike the LibreSign application repository, documentation branch numbers
refer to **LibreSign versions**, not to Nextcloud server versions.

Within each branch, edit pages directly under ``user_manual/``,
``admin_manual/`` or ``developer_manual/``. Add the new page to the
section's ``.. toctree::`` in its ``index.rst``. The ``main/`` directory
contains the site's landing and lifecycle information.

**Do not edit multiple copies of a page in the same branch.** A change in
``main`` does not alter an older released manual. To fix multiple releases,
backport the change to each relevant ``stableNN`` branch.

Contributing
------------

1. Open the documentation page for the intended LibreSign version.
2. Use **Edit on GitHub**, which selects that version's branch and file.
3. Make the RST change and update the section index if it is a new page.
4. Open a pull request against the **same branch**.
5. Review the generated preview and the Sphinx check.

An ordinary new RST page does not require creating a Python test or editing
versioning scripts. See `CONTRIBUTING.md
<https://github.com/LibreSign/documentation/blob/main/CONTRIBUTING.md>`_
for development and review instructions.

Local validation
----------------

Install the requirements and build the manual you changed::

   python -m pip install -r requirements.txt
   sphinx-build -n -W developer_manual _build/developer_manual

Replace ``developer_manual`` with ``admin_manual`` or ``user_manual`` as
appropriate. The documentation CI also checks links and the version's pinned
LibreSign OpenAPI contract. The application repository is the source of
truth for application compatibility, not the documentation branch name.

The repository and its content use the Creative Commons Attribution 3.0
Unported license. Every commit must have a DCO sign-off.

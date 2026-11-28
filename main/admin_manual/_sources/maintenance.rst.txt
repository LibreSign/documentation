Maintenance
=============

Recover identification documents of external signers
-----------------------------------------------------

Before LibreSign included the fix from
`#8368 <https://github.com/LibreSign/libresign/pull/8368>`__, identification
documents uploaded by signers without a Nextcloud account were written to the
``unauthenticated`` folder of the LibreSign app data, while their LibreSign
record pointed to the storage of the owner of the document being signed.
Those documents cannot be opened in Documents Validation, even after
upgrading.

The ``libresign:id-docs:recover`` command finds these documents and copies
them to the storage of their owner.

What the command checks
^^^^^^^^^^^^^^^^^^^^^^^

Only identification documents uploaded by external signers are checked. Each
one is reported with one of these statuses:

``affected``
   The document is in the ``unauthenticated`` app data folder, its owner and
   sign request are consistent, and it can be recovered.

``already_correct``
   The owner can already read the document. Nothing is changed. Documents
   recovered by an earlier run are reported like this.

``ambiguous``
   The records do not prove who the owner is, or recovering would touch other
   data: the owner differs from the owner of the signed document, the file is
   referenced by more than one LibreSign record, or the document already has a
   signed copy. Nothing is changed.

``unrecoverable``
   A required piece is missing: the LibreSign file record, the owner account,
   the sign request, the signed document or the stored file itself. Nothing is
   changed.

The output lists LibreSign record IDs and Nextcloud node IDs only. It does not
show file names, document contents or signer data.

Before you start
^^^^^^^^^^^^^^^^

- Back up the database and the Nextcloud data directory.
- Make sure the owner accounts have enough quota for the copies.
- Run the command as the web server user, like any other ``occ`` command.

Dry-run
^^^^^^^

By default the command does not change anything. Run it first to see what it
would do:

.. code-block:: bash

   sudo -E -u www-data php occ libresign:id-docs:recover

Recovery
^^^^^^^^

When the report looks right, run it again with ``--execute``:

.. code-block:: bash

   sudo -E -u www-data php occ libresign:id-docs:recover --execute

For each ``affected`` document, the command:

#. creates a new folder named after the date and ``recovered-id-doc-<file id>``
   inside the LibreSign folder of the owner, and stops if that folder is not
   in the owner's files;
#. copies the file into it;
#. compares the SHA-256 hash of the copy with the original and checks that the
   owner can read the copy;
#. updates the LibreSign record to the copy, inside a database transaction and
   only if the record did not change in the meantime.

The LibreSign file ID, UUID, identification document record and sign request
are kept. Documents recovered successfully are reported as ``recovered`` and
the table shows the new node ID.

Verification
^^^^^^^^^^^^

Open Documents Validation as an approver and open or download a recovered
document. Running the command again reports recovered documents as
``already_correct``.

The original files are not removed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The originals stay in the ``unauthenticated`` app data folder. Remove them
yourself after you have verified the recovered documents and your backup.

Errors and retry
^^^^^^^^^^^^^^^^

If a recovery step fails, the document is reported as ``failed`` and the
command exits with a non-zero status. The command removes the folder it
created for the copy and leaves the LibreSign record unchanged, so the
document is reported as ``affected`` again on the next run. Details are
written to the Nextcloud log.

A ``failed`` document with the reason ``owner storage not available`` belongs
to an owner whose Nextcloud files were never initialized, for example an
account that never logged in. The command does not write the copy anywhere
else. Ask the owner to log in once, then run the command again.

If the folder could not be removed, its node ID is shown in the *New node*
column. Delete it before running the command again, or a second copy will be
created.

If the command is interrupted, for example by a server restart, a
``recovered-id-doc-<file id>`` folder may stay behind without being referenced
by LibreSign. Run the dry-run again: a document still reported as ``affected``
was not switched to its copy, and that folder can be deleted.

Limitations
^^^^^^^^^^^

- Documents with a signed copy are not recovered.
- Deleted records are not rebuilt from file names. Documents whose records
  were deleted, for example to ask the signer to upload them again, are not
  found.
- Identification documents uploaded by users with an account were not
  affected by the original bug and are not checked.

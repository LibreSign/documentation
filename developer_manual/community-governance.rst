.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

Community governance and review policy (proposal)
=================================================

.. note::

   This proposal does not change current GitHub permissions or branch rules.
   Verify active rules before relying on approvals for merges.

LibreSign welcomes contributions and reviews from people outside the GitHub
organization. Employment at or membership in LibreCode coop is not required.

Community roles
---------------

* **Contributor:** anyone who reports issues, improves documentation, tests,
  submits pull requests or reviews public changes.
* **Community member:** someone invited after a first meaningful merged pull
  request, if the membership proposal is approved. Membership alone grants
  no repository write permission.
* **Reviewer:** a contributor trusted to provide substantial technical reviews
  and granted repository-scoped Write access. Their approval counts toward
  branch protections and they may merge when all protections are satisfied.
* **Maintainer:** an experienced reviewer with continuing responsibilities for
  architecture, project health, contributor support and releases. Maintainers
  may receive repository-scoped Maintain access, without rule bypass.

Organization owners and repository administrators are operational roles,
separate from community recognition. Neither reviewer nor maintainer status
grants Admin access or a bypass. Exceptions require their own justified and
auditable authorization.

Promotion
---------

As an initial reviewer eligibility guideline, a candidate may present two
meaningful merged pull requests and three substantive technical reviews of
other contributors' pull requests. Equivalent demonstrated experience is
acceptable. Counts trigger consideration, not automatic promotion.

A maintainer evaluates the evidence and records the decision and the
repositories covered. Contributors may apply directly even if automation
does not identify them. Rejections should contain reasons and an opportunity
for reconsideration.

A maintainer appointment additionally requires sound technical judgment,
constructive participation, support for contributors and willingness to
take continuing responsibility. A proposed selection process is nomination
by one maintainer and documented approval by two existing maintainers.
Cooperative membership is not a prerequisite.

Review and merge
----------------

Anyone may comment on or review public pull requests, subject to GitHub's
moderation settings. Reviews from people without write access are valuable
but do not ordinarily satisfy required approval counts.

The intended future branch policy requires two independent approvals, an
eligible code-owner approval, resolved conversations, and applicable CI and
DCO checks. Reviewers and maintainers may merge once every requirement passes,
but neither receives a bypass. Do not activate the new approval threshold
before enough active reviewers can meet it.

Substantive reviews consider behavior, security, regression tests,
compatibility and documentation where appropriate. A bare LGTM does not
by itself demonstrate reviewer qualification.

Administration and continuity
-----------------------------

Use GitHub team review assignment to distribute work fairly. Volunteers
can pause review assignment without losing community recognition. Review
repository access periodically, especially for inactive privileged accounts.

Bypasses are exceptional operational mechanisms, never a substitute for
working tests or reviews. Document each exception's identity, purpose,
scope and responsible owner before retaining it.

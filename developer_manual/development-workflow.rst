.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

Development workflow
====================

This page describes the durable contribution workflow for LibreSign. Repository
instructions such as ``AGENTS.md`` may add operational constraints for a
particular tool, but they should point back to this documentation instead of
duplicating it.

Choose and understand the work
------------------------------

Start from a GitHub issue whenever possible. Before implementing it:

- verify that the issue still matches the current code;
- check for existing pull requests or duplicate work;
- identify acceptance criteria, exclusions and real prerequisites;
- keep unrelated improvements out of the same change.

Large outcomes should be split into independently reviewable issues when useful.
Use blocking relationships only for real prerequisites.

Prepare the environment
-----------------------

Use the supported development environment described in
:doc:`getting-started/development-environment/index`.

The environment implementation may evolve, but contributors should not need to
maintain multiple independent Nextcloud Docker topologies for the same project.

Implement a focused change
--------------------------

Prefer the smallest coherent change that satisfies the issue.

Follow the current application architecture and contribution rules from the
base branch. Avoid unrelated refactors, dependency upgrades and formatting
churn unless they are required for the requested outcome.

Validate the behavior
---------------------

Use :doc:`getting-started/tests` to choose the relevant test path.

Prefer a focused regression test that fails under the unwanted behavior when
practical. Run narrow checks first, then broaden according to the changed
surface and current CI requirements.

Record which commands actually ran and which checks could not be run. A focused
test does not prove the whole project is green.

Review the final diff
---------------------

Before opening a pull request:

- inspect every changed file for unrelated changes;
- compare the result with the issue acceptance criteria;
- check error paths, permissions and compatibility where relevant;
- verify generated files and documentation when the changed contract requires
  them.

Commit and open the pull request
--------------------------------

Follow :doc:`getting-started/commits` for commit requirements and DCO.

Keep the pull request focused and make validation evidence easy to review:
reference the issue, summarize material implementation choices, list checks that
actually ran and describe known limitations when relevant.

A pull request remains subject to the repository's current review, CI and
branch policies.

After review or CI feedback
---------------------------

Re-evaluate feedback against the latest branch state before changing code.
When CI fails, identify the causal failure before adding retries, sleeps,
dependency pins or suppressions.

Follow-up work that is useful but not required for the current issue should be
tracked separately instead of expanding the pull request indefinitely.

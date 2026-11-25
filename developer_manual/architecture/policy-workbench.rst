.. SPDX-FileCopyrightText: 2026 LibreCode coop and contributors
.. SPDX-License-Identifier: CC-BY-3.0

Policy Workbench architecture
=============================

This page explains how LibreSign policies are defined, stored, resolved,
enforced and presented in the Policy Workbench. It is written for developers
who know PHP and TypeScript but have not worked on the Workbench before.

Use the application repository as the source of truth for current class names
and values: `LibreSign/libresign <https://github.com/LibreSign/libresign>`_.
Policy code lives in ``lib/Service/Policy/`` (backend) and
``src/views/Settings/PolicyWorkbench/`` (frontend).

What Policy Workbench is
------------------------

A *policy* is a named setting that changes how LibreSign behaves, for example
the signature flow, the footer or the PDF certification level. Each policy has
a stable key, a default value and a set of allowed values.

The same policy can be configured at several levels. An administrator can set
an instance-wide value, a group can refine it, and a user can express a
preference, as long as the level above permits it. The backend combines these
values into one *resolved policy* for the current actor. That result carries
the effective value, where the value came from, and what the actor may do with
it.

The Policy Workbench is the administration screen for these settings. It lets
administrators and delegated group administrators create, change and remove
rules. It is a presentation of backend state. It does not decide what is
allowed.

The backend is the trust boundary. Permissions, resolution, delegation and
inheritance are enforced there, and frontend checks only shape the interface.
This follows the boundary described in :doc:`../architecture`.

Policy scopes
-------------

The scopes are ordered from broadest to narrowest:

System
   The instance-wide level. A policy that has no explicit system rule uses its
   built-in default.

Group
   A rule bound to a Nextcloud group. A rule applies to a user through the
   user's group membership.

User
   A rule that an administrator assigns to a specific user, and a personal
   preference the user saves for themselves. These are separate stored values
   (see `Personal preferences`_).

A signature request can also carry a value for a single request. This
*request override* is not a stored rule. It exists only while the request is
resolved.

A policy definition lists the scopes it supports. A policy can be limited to
the system scope, and the backend rejects writes at a scope the definition does
not support.

The resolved policy reports the origin of its value as a *source scope*. The
values a client can see are ``system`` (built-in default), ``global`` (an
explicit system rule), ``group``, ``user_policy`` (a rule assigned to a user),
``user`` (a personal preference) and ``request``.

Group rules can be evaluated for one group only. A request that names an
*active group context* resolves against that group instead of all groups of
the user, and the backend rejects a context for a group the actor does not
belong to.

Circles are not part of resolution. The source interface has a hook for them,
but the resolver does not load or apply circle rules.

Effective policy resolution
---------------------------

Resolution produces one resolved policy per key for a given actor context. The
context holds the target user, the groups, the actor role, the optional active
group scope and any request values.

The resolver starts from the built-in default and applies each layer in this
order:

1. The system rule.
2. Group rules.
3. The rule an administrator assigned to the user.
4. The user's personal preference.
5. The request value.

Each layer carries three controls that shape what lower layers can do:

``allowChildOverride``
   Whether lower layers may change the value. When it is false, the value is
   locked and lower layers are ignored.

``visibleToChild``
   Whether lower layers see the policy at all.

``allowedValues``
   The values lower layers may choose from. Restrictions from several layers
   are intersected.

A lower layer only applies when every layer above it still allows
overriding, and when its value is allowed and valid for the definition. When a
personal preference or a request value is not applied, the resolved policy
reports the scope that blocked it in ``blockedBy``. A stored personal
preference that the policy no longer permits is cleared. A stored system or
group value that is invalid is skipped and the value below it stays in effect.

Some policies resolve in *value choice* mode. For these, group rules do not
replace the value. They contribute the choices that users in those groups may
pick from, and the resolver offers the union of the choices.

A request value follows the same rules as a lower layer, and it also needs the
actor's permission to override the policy for a request. A value that a
document stored earlier is replayed without asking the current actor again,
because it was authorized when it was submitted.

The result also tells the client what the actor may do: whether the policy is
visible, whether the actor can manage group rules, whether the actor can save
a personal default and whether a request can override it.

Delegation and customization
----------------------------

Delegation controls how much of a policy lower levels can customize.

At each level, the author of a rule decides whether lower levels may override
it (``allowChildOverride``), see it (``visibleToChild``) and which values they
may choose. A system administrator can lock a value for everyone, or leave it
open.

Group administrators are Nextcloud sub-administrators. They can manage group
rules only after the system administrator explicitly delegates that
capability. The delegation is an explicit system rule that allows lower levels
to override. A built-in default alone does not delegate anything.

Group rules remember who created them. A policy can decide that rules created
by a system administrator are hidden from group administrators, or that they
cannot be edited or deleted by them. Policies that support *group-admin
delegation* keep the system-created rule and the group administrator's own
override side by side, so one does not overwrite the other.

A group administrator is limited to the groups they manage. Managing the rules
of another user is limited to users who share a managed group.

Backend enforcement
-------------------

Every write passes through ``PolicyService``. Before saving, the service:

- checks that the definition supports the scope;
- checks that the actor may manage the target (system, group or user);
- normalizes the value and validates it against the definition, including
  checks that apply only when saving, such as rejecting an unsafe template;
- for compound policies, validates the whole family of values together.

Controllers apply an earlier gate. System-level routes do not allow non-admin
access, and group and user routes ask the management-scope service whether the
actor can manage that target before calling the service. Rejections return a
forbidden or bad-request response.

Reads are filtered too. The effective-policies endpoint returns the state
resolved for the current actor, and rule counts and listings omit group rules
the actor must not see.

Request-level behavior is enforced where a signature request is created or
updated. A policy that affects a request has a file policy applier. The
applier reads the request values and resolves the policy for the file. It
refuses a request value the resolved policy does not allow, and it can store
the effective value on the file. A policy declares a
*request lifecycle*:

``request_snapshot``
   The value is stored on the request when it is created and stays fixed once
   the request enters the signing flow, even if the policy changes later.
   ``FrozenFilePolicySnapshotResolver`` reads that stored value for a file or
   an envelope.

``runtime``
   The value is read from the current policy whenever it is needed, so a change
   reaches requests that were already sent.

Authorization that depends on a policy uses the resolved value. For example,
``RequestSignAuthorizationService`` decides from the resolved request-access
policy whether a user belongs to a group that may request signatures. It
denies a missing user.

Public validation pages expose a limited projection of the resolved policies,
and they prefer the stored snapshot over the current policy when one exists.

Frontend representation
-----------------------

The frontend reads the effective policies once through the Pinia policies
store (``src/store/policies.ts``), which is seeded from the initial page state
and refreshed from the effective-policies endpoint. It exposes the resolved
state and the write calls. It does not recompute the resolution.

When a refresh fails, the store keeps the last values for display but stops
granting request overrides. A client that cannot confirm the current policy
does not offer an override.

The Workbench catalog is built from one *real definition* per policy
(``settings/realDefinitions.ts``). A definition holds presentation concerns:
title, description, category, the editor component, how to summarize a value,
and how to create an empty draft. Policy-specific frontend behavior stays in
its own folder under ``settings/``. Backend-only and helper policies have no
definition, so they do not appear as cards.

The Workbench works in two view modes. System administrators see the full
catalog. Group administrators see the policies the backend reports as editable
or delegable to them. The interface follows the flags from the resolved state,
such as ``editableByCurrentActor`` and ``canSaveAsUserDefault``. Hiding a card
or a button is a convenience. The backend still rejects the request if the
actor is not allowed.

Compound policies
-----------------

Some settings only make sense together. A *compound policy* has a parent policy
and companion policies, for example signing mode with its worker configuration,
or the signature stamp with metadata collection. Request expiration and
signature rejection are also compound.

The backend marks the relationship with a parent key and a list of composite
children, and it exposes compound write endpoints. A compound write validates
the complete resulting configuration before it stores any key, so the outcome
does not depend on the order of the values.

The frontend presents a compound policy as one card. A definition provides a
function that composes the member values into one editor value and another that
splits the editor value back into member values. The Workbench saves all
members through one compound call per target and clears every member together
when a rule is removed.

Personal preferences
--------------------

A personal preference is a value a user saves for themselves. It is the lowest
stored layer and applies only when every layer above it allows overriding.

Not every policy supports it. A definition declares whether it supports
personal preferences, and a preference is accepted only when the resolved
policy allows the user to save a personal default. A policy that is
administration-only never accepts one, and a stored preference that the policy
no longer allows is cleared during resolution.

The Preferences screen shows a policy only if it is part of the Workbench
catalog, the backend reports that it supports personal preferences, and the
actor can save a default or already has one. Policies that an administrator
assigns to a user without personal preference support, such as time stamping
and revocation settings, do not appear there.

Adding a new policy
-------------------

Adding a policy follows the extension path that existing policies use. Keep
backend behavior with the policy provider and frontend behavior with the
policy's Workbench module.

1. Create a provider under ``lib/Service/Policy/Provider/<Name>/``. It
   implements ``IPolicyDefinitionProvider`` and returns a ``PolicySpec`` with
   the key, default value, allowed values, normalizer, supported scopes and the
   two decisions every policy must make: whether a request may override it, and
   its request lifecycle.
2. Register the key in ``PolicyProviders::BY_KEY``. The registry resolves
   definitions from this map.
3. If the policy changes how a signature request is created or processed, add a
   file policy applier in the provider's ``FilePolicy`` folder. The applier is
   discovered by its name, which is built from the provider class name.
4. Add a real definition under ``src/views/Settings/PolicyWorkbench/settings/``
   with its editor component, and list it in
   ``settings/realDefinitions.ts`` with a category. Skip this step for backend-only and helper
   policies.
5. Add tests for each layer you touched (see the next section).

Do not move enforcement into the frontend definition. Define who may manage the
policy, what a lower scope may do and how delegation works in the backend
definition.

Testing expectations
--------------------

Choose the narrowest layer that proves the behavior, and add tests at the trust
boundary you change. See :doc:`../getting-started/tests` for the commands.

Backend unit tests, under ``tests/php/Unit/Service/Policy/``:

- ``Runtime/DefaultPolicyResolverTest.php`` covers layer order, locks, hidden
  policies, request values and personal preferences.
- ``PolicyServiceTest.php`` covers who may save or clear which scope.
- ``Runtime/PolicySourceTest.php`` covers how values are stored and read back.
- The ``Provider/`` tests cover the rules of a single policy.
- The applier and snapshot tests cover request values and frozen requests.

Controller tests, in ``tests/php/Unit/Controller/PolicyControllerTest.php``,
cover the response codes and the forbidden paths.

Frontend unit tests, under ``src/tests/views/Settings/PolicyWorkbench/`` and
``src/tests/store/policies.spec.ts``, cover the catalog, the compound helpers,
each policy's definition and the store, including a failed refresh.

Browser tests, in ``playwright/e2e/policy-*.spec.ts``, exercise the Workbench as
different personas, such as a system administrator, a group administrator and an
end user.

A change that touches resolution, delegation or visibility needs a negative
test: the case where a lower scope tries to weaken a higher scope and must be
refused.

Related architecture
--------------------

- :doc:`../architecture` for the repository map and responsibility boundaries.
- :doc:`../getting-started/tests` for test layers and commands.
- :doc:`../getting-started/development-environment/index` for a runtime to try
  the Workbench.
- :doc:`../error-handling` for exception types and status codes returned by the
  policy endpoints.

# Staff delivery/authorization addendum v1.0.1

PROPOSED. Exact nine registrations/actions/fields/filter/search/permissions from
R01 [admin-inventory](../../../docs/acceptance/MS7-MIG-R01/admin-inventory.json)
are copied by reference in the route map; every operation is included below.
Seven Content models remain view-only even for superusers. User/Group are full
existing administration; Permission has no standalone CRUD. StudentProfile,
IdentityReceipt and LoginWindow are not registered or newly exposed as staff CRUD.

Every staff request authenticates active User first: anonymous/inactive401,
nonstaff403; then is_staff and matching model permission (superuser passes model
permission). View permits view OR change as Django ModelAdmin does; source-managed
Content has no add/change/delete regardless of assigned permission. Detail and
history use the same view gate. Action permissions checked server-side per item,
not by hiding controls. Mutation CSRF and same-origin mandatory; safe400/403/404/
409/503 envelopes, private no-store. Reject unexpected DTO fields/relations.

| Resources | Required operations / DTO / permission |
| --- | --- |
| grades, subjects, sections, pages, publications, media_assets, redirects | list, detail, search, baseline list filters/order, history read; content.view_<model> OR content.change_<model>; fields exactly inventoried including ContentPage.source_location. All mutation paths forbidden403. |
| users | list/search/filter/detail/history, create, edit username/email/first_name/last_name/active/staff/superuser/last_login/date_joined, direct permissions and groups, usable/unusable password creation, password change, guarded single delete and delete-selected. auth.view/change/add/delete_user by action. |
| groups | list/search/detail/history, create/edit name and permission assignments, guarded single delete/delete-selected. auth.view/change/add/delete_group by action. |
| permission selectors | read only under the applicable combined User-create gate, auth.change_user, or auth.add/change_group for their form; expose id/name/codename/contenttype only; no independent registered permission admin CRUD. |

Baseline UserAdmin allows a staff actor with auth.change_user to edit role flags,
groups/direct permissions and password (even privilege-bearing fields). Do not
silently substitute a superuser-only policy or self-escalation safeguard and call
that baseline parity. Any stricter rule requires an explicit security scope
decision and updated positive/negative expectations before V03 acceptance.
Current mapping preserves baseline permissions and makes that risk reviewable.
Staff user creation requires auth.add_user AND auth.change_user, matching
Django UserAdmin._add_view and the parent add gate. Group creation requires
auth.add_group. User edit/password uses auth.change_user; delete
requires auth.delete_user. Groups change permission assignments with
auth.change_group. Related object selectors and choices mirror baseline forms.

Existing UserAdmin password form supports setting a usable password and disabling
password authentication. usable_password=true requires matching password1/2 and
the baseline password validators; false requires explicit confirm_disable=true
(Django's unset-password confirmation), stores the unusable marker, and discards
password fields. Disabling requires the existing user to have a usable password,
as in the baseline form; otherwise return a safe state conflict. Never accept an
accidental unchecked/omitted disable choice.
The admin site's own password change is also required: active staff may submit
old_password/new_password1/new_password2 without auth.change_user. Verify the old
password, matching new values and validators; preserve the current session with
update_session_auth_hash and rotation, invalidating other sessions. Changing
another user's password does not rotate the actor's session. No response echoes
password fields, encoded password, or session tokens. These are adapter contracts,
not new runtime endpoints.

StaffUserDTO includes only safe id, username, names, email, role/active flags,
date_joined/last_login, group IDs/direct permission IDs, has_usable_password;
never encoded_password/session/receipt/key_digest. Password request is writeOnly
and never echoed. Content detail is closed typed fields per model, not arbitrary
ORM serialization. A proposed private StaffRecordDTO carries model+fields using
model-specific schemas; no dynamic additionalProperties bag. Staff history
DTO timestamp, actor ID, action and sanitized change summary; preserve historical
admin log rows/actor links/object IDs; no plaintext password or raw request.

All single/bulk delete requests support an explicit confirmation token tied to
the displayed IDs and current revision; preflight permissions and PROTECT in the
same transaction. Protected User/Profile/Receipt/Grade dependencies yield safe
409 STATE_CONFLICT and zero partial deletion. Group/user association cleanup
matches Django collector; protected student history survives. Search/filter/
pagination must preserve baseline results and permission behavior, not only
display a hardcoded fixture table. CSRF/session/password revocation/audit failure
cannot return success. Current Content changes still occur via publication CLI.

New namespace /api/v1/staff/... in separate OAS is proposed adapter-only.
Canonical frozen37-operation OAS remains unchanged. Native frontend staff paths
/admin/ and model list/detail/forms preserve baseline navigation through route
adapters, no new CMS. HTML login redirect behavior can stay presentation-specific;
JSON uses401/403, never HTML login302. Full admin URL patterns and operation
metadata are in implemented-routes-v1.json, including password change/history/
delete-selected. CLI cannot replace these accepted UI capabilities.

List query contract: q maps exactly to inventoried search_fields, and named
filter__<inventoried list_filter> maps to the same model filter, strict bool/ID/
page_type validation without coercion. Unknown/repeated singleton params400.
Preserve baseline default ordering from registered ModelAdmin or model Meta;
the original Django o column index maps through inventoried list_display to a
validated ordered field list in the frontend adapter. No arbitrary SQL ordering
string. Staff pagination default20/max100, cursor bound to authenticated staff,
resource/search/filter/order and page_size; preserve baseline unique ordering
and append descending PK only when required by Django deterministic ordering.
Keyset pagination avoids offset skips but does not promise an immutable snapshot
while records are edited; mutation consistency is a later implementation test. This is separate from anonymous grades cursor.
Delete preview GET for single/bulk listed IDs returns private confirmation token
bound to actor, IDs/current record digest/expiry; POST rechecks it and permissions/
PROTECT under locks. Preview performs no domain mutation, blocked protected
deletion remains inspectable without leaking records to an unauthorized actor.


## Review amendments B01/B03/B04/B05/B06

The User creation button/form and POST use the combined add_user AND change_user
gate, even if Django's generic add button alone is visible. add-only, change-only,
neither, inactive and nonstaff must not create a user. Superuser follows baseline.

Boolean query wire values, including filter__is_permanent and filter__is_active,
are exactly the singleton URI strings true/false, decoded into JSON true/false.
Reject0/1, uppercase, empty and repeated values with400. Native Django admin
is_permanent__exact=0/1 is translated explicitly; temporary redirects remain
selectable. JSON Schema/OAS use boolean, never positive integer/coercion.

Each of the nine list operations declares singleton sort. Grammar:
sort=default OR [-]field(,[-]field)*. Minus means descending; absence means
ascending. No plus, spaces, empty terms, repeated field (even opposite sign),
unknown columns, relation injection or raw SQL. Omitted/default selects native
ordering. Per-resource allowed fields and default/effective orders are defined in
[staff-list-policy](staff-list-policy-v1.json) and OAS x-sort-contract. Group's
__str__ column has no native sort field: only omitted/default is allowed, with
baseline name ordering. Other fields map native list_display columns, including
FK sorting through referenced model Meta.ordering rather than display strings.
Explicit terms precede ModelAdmin queryset ordering; retain the exact unique-key
deterministic rule and descending PK where needed. Preserve PostgreSQL collation
and ASC NULLS LAST / DESC NULLS FIRST; SQLite emulates these for compatibility.
Native o indexes account for the action checkbox only if available to the actor;
they translate into named fields/directions, never become SQL fragments.

Cursor binds actor ID, authorization-scope revision, resource, exact q, normalized
filters, expanded effective sort keys/directions and page_size. It signs the
ordered last values with explicit NULL markers. authorization_scope_revision is
a digest of current active/staff/superuser flags and sorted effective permission
codes, recomputed at authorization; it needs no new persisted permission column.
Mismatched/tampered cursors400;
every field/direction/filter/page-size change starts a new list. Multi-sort and
ties must compare to Django order, with nullable relations and mixed directions.

GET /api/v1/staff/users/{id}/group_choices/ returns only group id/name choices for
the existing User edit form under active staff + auth.change_user. It validates
that the target User exists (404 otherwise), returns all groups ordered by name
as the baseline form queryset, private/no-store; no pagination silently omits
choices. View-only User permission403. It does not require Group view/change,
and grants no access to group administration/list/detail/history/write. Groups
cannot be assigned in baseline creation form (add_fieldsets omits them); group
choices are not exposed there. Existing groups on the edited User remain visible
and editable under change_user. No new group creator or privileged popup.

Publication state GET is read-only under the same ContentPage view/change gate;
see content-v1.md. It does not authorize a publisher action or Group administration.

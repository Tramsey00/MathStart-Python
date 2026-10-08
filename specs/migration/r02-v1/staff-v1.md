# Staff delivery/authorization addendum v1.0.0

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
| permission selectors | read only under auth.add/change_user or auth.add/change_group for their form; expose id/name/codename/contenttype only; no independent registered permission admin CRUD. |

Baseline UserAdmin allows a staff actor with auth.change_user to edit role flags,
groups/direct permissions and password (even privilege-bearing fields). Do not
silently substitute a superuser-only policy or self-escalation safeguard and call
that baseline parity. Any stricter rule requires an explicit security scope
decision and updated positive/negative expectations before V03 acceptance.
Current mapping preserves baseline permissions and makes that risk reviewable.
Staff creates use auth.add_user; edit/password uses auth.change_user; delete
requires auth.delete_user. Groups change permission assignments with
auth.change_group. Related object selectors and choices mirror baseline forms.

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
resource/search/filter/order and page_size; append PK tie-break so edits/deletion
cannot cause offset skips. This is separate from anonymous grades cursor.
Delete preview GET for single/bulk listed IDs returns private confirmation token
bound to actor, IDs/current record digest/expiry; POST rechecks it and permissions/
PROTECT under locks. Preview performs no domain mutation, blocked protected
deletion remains inspectable without leaking records to an unauthorized actor.

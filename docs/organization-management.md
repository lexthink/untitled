# Organization Management

> **Note:** This document is a proposal for future implementation. None of this is implemented yet.

## Onboarding model (proposed)

B2B invite-only:

1. A potential customer requests a demo
2. A superuser creates the organization and its owner account
3. The owner invites their team members

No public signup. Users cannot create organizations themselves. Every organization is a verified customer.

## User access

### How users join organizations

**By invitation (recommended):**
1. Owner/admin invites a user by email
2. System sends an email with an invite link (token-based)
3. If the user exists, they accept and a membership is created
4. If the user doesn't exist, they sign up and the membership is created on registration

**By email domain (optional):**
- Users with a matching email domain (e.g. `@company.com`) can join automatically
- Configured per organization
- Useful for large organizations

**By request (optional):**
- User requests to join an organization
- An admin approves or rejects

### Invitation model

```python
class Invitation(AbstractModel):
    organization = ForeignKey(Organization, on_delete=CASCADE)
    email = EmailField()
    role = CharField(choices=Role)
    invited_by = ForeignKey(User, on_delete=CASCADE)
    token = CharField(unique=True)  # UUID or random token
    expires_at = DateTimeField()
    accepted_at = DateTimeField(null=True)
```

Key behaviors:
- Expires after a configurable period (e.g. 7 days)
- Can be revoked (deleted) before acceptance
- One active invitation per email per organization
- Accepting creates the Membership (and User if needed)

### Invitation flow

```
Owner creates invite
  → System sends email with link: /invite/<token>
    → User clicks link
      → If logged in and user exists: create Membership, redirect to org
      → If not logged in and user exists: redirect to login, then accept
      → If user doesn't exist: redirect to signup, then accept
```

## What each role can do

### Owner

- View all members of their organization
- Invite new members
- Change member roles (admin, member)
- Remove members
- Transfer ownership to another member
- Delete the organization

### Admin

- View all members of their organization
- Invite new members
- Change member roles (only to member, not owner)
- Remove members (except owner)

### Member

- View members of their organization (limited info: name, email, role)
- Leave the organization

## Listing users

Users should **never** be listed directly. Always list through memberships:

```python
# Correct — scoped to organization
@router.get("/members/", response=list[MemberSchema])
@require_roles(Role.OWNER, Role.ADMIN, Role.MEMBER)
def list_members(request):
    return request.membership.organization.memberships.select_related("user").all()

# Wrong — exposes all users
@router.get("/users/")
def list_users(request):
    return User.objects.all()
```

The API should only expose user data through the membership context. A member schema should include:
- User name
- User email
- Role in the organization
- Joined date (membership created_at)

It should NOT expose:
- Superuser status
- Other organization memberships
- Internal user fields (password, last_login, etc.)

## Ownership transfer

- Only the current owner can transfer
- The target must be an existing member
- The old owner becomes admin (not removed)
- There must always be at least one owner

```python
@router.post("/transfer-ownership/{user_id}/")
@require_roles(Role.OWNER)
def transfer_ownership(request, user_id: UUID):
    new_owner = get_membership_or_404(request.membership.organization, user_id)
    old_owner = request.membership

    new_owner.role = Role.OWNER
    new_owner.save()

    old_owner.role = Role.ADMIN
    old_owner.save()
```

## Removing members

- Owners cannot be removed (must transfer ownership first)
- Admins can remove members but not other admins or owner
- Removing a membership does NOT delete the user or their data
- The `created_by` references on organization data remain intact

## Deleting an organization

- Only the owner can delete
- Requires confirmation (e.g. type organization name)
- Should have a grace period (soft delete) before hard delete
- Hard delete drops the PostgreSQL schema (`DROP SCHEMA CASCADE`)
- All memberships are deleted
- Users are NOT deleted — they may belong to other organizations

## Audit log (recommended)

Track important actions for security and debugging:

```python
class AuditLog(AbstractModel):
    organization = ForeignKey(Organization, on_delete=CASCADE)
    user = ForeignKey(User, on_delete=SET_NULL, null=True)
    action = CharField()  # "invite_sent", "member_removed", "role_changed", etc.
    target_user = ForeignKey(User, on_delete=SET_NULL, null=True, related_name="+")
    metadata = JSONField(default=dict)  # extra context
```

This model should be in `SHARED_APPS` (public schema) since it references users and organizations.

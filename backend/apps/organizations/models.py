from django.db.models import CASCADE
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import ForeignKey
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django_tenants.models import DomainMixin
from django_tenants.models import TenantMixin

from apps.users.models import User
from apps.utils.models import AbstractModel

from .enums import Role


class Domain(AbstractModel, DomainMixin):
    pass


class Organization(AbstractModel, TenantMixin):
    name = CharField(_("name"), max_length=255)
    auto_create_schema = True

    def __str__(self) -> str:
        return self.name


class Membership(AbstractModel):
    user = ForeignKey(
        User,
        verbose_name=_("user"),
        related_name="memberships",
        on_delete=CASCADE,
    )
    organization = ForeignKey(
        Organization,
        verbose_name=_("organization"),
        related_name="memberships",
        on_delete=CASCADE,
    )
    role = CharField(
        verbose_name=_("role"),
        max_length=20,
        choices=Role,
        default=Role.MEMBER,
    )
    is_default = BooleanField(
        verbose_name=_("default"),
        default=False,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "organization"],
                name="unique_membership",
            ),
        ]

    def save(self, *args, **kwargs):
        is_new = not self.__class__.objects.filter(pk=self.pk).exists()
        if is_new and not self.__class__.objects.filter(user=self.user).exists():
            self.is_default = True
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user} - {self.organization} ({self.role})"

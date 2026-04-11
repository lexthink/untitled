from django.utils.translation import gettext_lazy as _
from model_utils.fields import AutoCreatedField
from model_utils.fields import AutoLastModifiedField
from model_utils.models import UUIDModel


class AbstractModel(UUIDModel):
    """
    This abstract base class all models
    """

    created_at = AutoCreatedField(_("created at"))
    updated_at = AutoLastModifiedField(_("updated at"))

    def save(self, *args, **kwargs):
        """
        Overriding the save method in order to make sure that
        updated_at field is updated even if it is not given as
        a parameter to the update field argument.
        """
        update_fields = kwargs.get("update_fields")
        if update_fields:
            kwargs["update_fields"] = set(update_fields).union({"updated_at"})

        super().save(*args, **kwargs)

    class Meta:
        abstract = True

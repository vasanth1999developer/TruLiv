import uuid
from contextlib import suppress

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils import timezone

from apps.common.helpers import file_upload_path
from apps.common.managers import (
    ArchivableObjectManagerQuerySet,
    BaseObjectManagerQuerySet,
    SoftDeleteObjectManagerQuerySet,
    StatusModelObjectManagerQuerySet,
)
from apps.common.model_fields import AppImageField

# top level config
COMMON_CHAR_FIELD_MAX_LENGTH = 512
COMMON_NULLABLE_FIELD_CONFIG = {  # user for API based stuff
    "default": None,
    "null": True,
}
COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG = {  # user for Form/app based stuff
    **COMMON_NULLABLE_FIELD_CONFIG,
    "blank": True,
}


class BaseModel(models.Model):
    """
    Contains the last modified and the created fields, basically
    the base model for the entire app.

    ********************* Model Fields *********************
    PK -
        id
    Unique -
        uuid
    Datetime -
        created_at
        modified_at
    """

    # unique id field
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    # time tracking
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # custom manager
    objects = BaseObjectManagerQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        abstract = True

    @classmethod
    def get_model_fields(cls):
        """
        Returns all the model fields. This does not
        include the defined M2M & related fields.
        """

        return cls._meta.fields

    @classmethod
    def get_all_model_fields(cls):
        """
        Returns all model fields, this includes M2M and related fields.
        Note: The field classes will be different & additional here.
        """

        return cls._meta.get_fields()

    @classmethod
    def get_model_field_names(cls, exclude=[]):  # noqa
        """Returns only the flat field names of the model."""

        exclude = ["id", "created_by", "created", "modified", *exclude]
        return [_.name for _ in cls.get_model_fields() if _.name not in exclude]

    @classmethod
    def get_model_field(cls, field_name, fallback=None):
        """Returns a single model field given by `field_name`."""

        with suppress(FieldDoesNotExist):
            return cls._meta.get_field(field_name)

        return fallback


class BaseCreationModel(BaseModel):
    """
    Contains the created_by field.

    ********************* Model Fields *********************
    PK -
        id
    FK -
        created_by
    Unique -
        uuid
    Datetime -
        created_at
        modified_at
    """

    # by whom
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="created_by_%(class)s",
        on_delete=models.SET_DEFAULT,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    class Meta:
        abstract = True


class BaseCreationAndModificationModel(BaseCreationModel):
    """
    Contains the created_by and modified_by fields along with datetime fields.

    ********************* Model Fields *********************
    PK -
        id
    FK -
        created_by
        modified_by
    Unique -
        uuid
    Datetime -
        created_at
        modified_at
    """

    # by whom
    modified_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="modified_by_%(class)s",
        on_delete=models.SET_DEFAULT,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    class Meta:
        abstract = True


class StatusModel(BaseModel):
    """
    An abstract base model that provides `is_active` field,
    as well as a custom QuerySet for active objects.

    ********************* Model Fields *********************
    PK -
        id
    Unique -
        uuid
    Datetime -
        created_at
        modified_at
    Bool -
        is_active
    """

    is_active = models.BooleanField(default=True)

    # custom manager
    objects = StatusModelObjectManagerQuerySet.as_manager()

    class Meta(BaseModel.Meta):
        abstract = True


class SoftDeleteModel(BaseModel):
    """
    An abstract base model that provides `is_deleted` field,
    as well as a custom QuerySet for soft-deleted objects.

    ********************* Model Fields *********************
    PK -
        id
    Unique -
        uuid
    Datetime -
        created_at
        modified_at
    Bool -
        is_deleted
    """

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    # custom manager
    objects = SoftDeleteObjectManagerQuerySet.as_manager()

    class Meta(BaseModel.Meta):
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft deletes obj."""

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()


class BaseCUDSoftDeleteModel(BaseCreationAndModificationModel, SoftDeleteModel):
    """
    Contains the created_by, modified_by & deleted_by fields along with datetime fields.

    ********************* Model Fields *********************
    PK -
        id
    FK -
        created_by
        modified_by
        deleted_by
    Unique -
        uuid
    Datetime -
        created_at
        modified_at
        deleted_at
    Bool -
        is_deleted
    """

    # by whom
    deleted_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="deleted_by_%(class)s",
        on_delete=models.SET_DEFAULT,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    class Meta:
        abstract = True


class BaseCUDArchivableModel(BaseCUDSoftDeleteModel, SoftDeleteModel, StatusModel):
    """
    Contains the created_by, modified_by & deleted_by fields along with datetime fields.

    ********************* Model Fields *********************
    PK -
        id
    FK -
        created_by
        modified_by
        deleted_by
    Unique -
        uuid
    Datetime -
        created_at
        modified_at
        deleted_at
    Bool -
        is_deleted
        is_active
    """

    # custom manager
    objects = ArchivableObjectManagerQuerySet.as_manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft deletes obj."""

        self.is_deleted = True
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()


class BaseArchivableModel(StatusModel, SoftDeleteModel):
    """
    An abstract base model that provides `is_active` and `is_deleted` fields,
    as well as a custom QuerySet for soft-deleted and active objects.
    Any model that inherits from this class will have `is_active`
    and `is_deleted` fields, and can use the `objects` manager
    to access the custom QuerySet methods for soft-deleted
    and active objects.

    Used in model - User

    ********************* Model Fields *********************
    PK -
        id
    Unique -
        uuid
    Datetime -
        created_at
        modified_at
    Bool -
        is_active
        is_deleted
    """

    # custom manager
    objects = ArchivableObjectManagerQuerySet.as_manager()

    class Meta(BaseModel.Meta):
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft deletes obj."""

        self.is_deleted = True
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()


class FileOnlyModel(BaseModel):
    """
    Parent class for all the file only models. This is used as a common class
    and for differentiating field on the run time.

    This will contain only:
        file = model_fields.AppFileField(...)

    This model is then linked as a foreign key where ever necessary.

    ********************* Model Fields *********************
    PK -
        id
    Unique -
        uuid
    Datetime -
        created_at
        modified_at
    """

    class Meta(BaseModel.Meta):
        abstract = True


class AppImageModel(FileOnlyModel):
    """Contains AppImageField."""

    image = AppImageField(
        max_size=5,
        upload_to=file_upload_path,
    )

    class Meta(FileOnlyModel.Meta):
        abstract = True

    @property
    def file_url(self):
        """Returns the image url if available."""

        return self.image.url if self.image else None


class DraftModel(models.Model):
    """
    Contains the is_draft field.

    ********************* Model Fields *********************
    Bool -
         is_draft
    """

    is_draft = models.BooleanField(default=True)

    class Meta:
        abstract = True


class ArchiveModel(models.Model):
    """
    Contains the is_archive field

    ********************* Model Fields *********************
    Bool -
        is_archive
    """

    is_archive = models.BooleanField(default=False)

    class Meta:
        abstract = True


class UniqueIdentityBaseModel(models.Model):
    """
    Contains unique name field.

    ********************* Model Fields *********************
    Unique -
        name
    """

    name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)

    class Meta:
        abstract = True


class IdentityBaseModel(BaseModel):
    """
    Contains name field.

    ********************* Model Fields *********************
    Char -
        name
    """

    name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH)

    class Meta:
        abstract = True


class DescriptionModel(models.Model):
    """
    Contains description field.

    ********************* Model Fields *********************
    TextField -
            description

    """

    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    class Meta:
        abstract = True

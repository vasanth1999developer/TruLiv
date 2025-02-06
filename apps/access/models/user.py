from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.managers import UserManager
from apps.common.model_fields import AppPhoneNumberField
from apps.common.models.base import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseArchivableModel,
    BaseCreationModel,
)
from apps.properties.choices import GenderChoices, RoleTypeChoices


class User(AbstractUser, BaseArchivableModel):
    """
    User model for the application...

    ********************************  Model Fields ********************************
    pk                  - id
    uuid                - uuid
    charField           -  first_name, last_name,
    DateTimeField       - created_at, modified_at, last_login, date_joined, deleted_at
    EmailField          - email
    PhoneNumberField    - phone_number
    BooleanField        - is_superuser, is_staff, is_active, is_deleted
    """

    username = None
    phone_number = AppPhoneNumberField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG, unique=True)
    first_name = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    last_name = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    gender = models.CharField(
        choices=GenderChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
    )
    email = models.EmailField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    role = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        choices=RoleTypeChoices.choices,
        default=RoleTypeChoices.guest,
    )
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return str(self.phone_number)

    class Meta(BaseCreationModel.Meta):
        default_related_name = "related_users"

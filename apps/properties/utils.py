import random

from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import Count

from apps.properties.models.properties import Bed


def allocate_bed(booking, user):
    """Allocate a bed to the user based on availability and booking rules."""
    try:
        with transaction.atomic():
            available_beds = Bed.objects.select_for_update().filter(
                property_room_type__property=booking.property, room_type=booking.room_type, is_available=True
            )
            if not available_beds.exists():
                raise Exception("No available beds in this property and room type.")
            total_rooms = booking.property.related_property_room_types.filter(room_type=booking.room_type).count()
            total_empty_rooms = available_beds.values("property_room_type").distinct().count()
            bed = None
            if total_empty_rooms == total_rooms:
                bed = available_beds.first()
            else:
                vacant_rooms = (
                    available_beds.values("property_room_type")
                    .annotate(available_count=Count("id"))
                    .order_by("-available_count")
                )
                if vacant_rooms.exists():
                    room_id = vacant_rooms.first()["property_room_type"]
                    bed = available_beds.filter(property_room_type_id=room_id).first()
                elif available_beds.count() > 1:
                    bed = random.choice(list(available_beds))
                else:
                    bed = available_beds.first()
            if not bed:
                raise Exception("Bed allocation failed. No suitable bed found.")
            bed.is_available = False
            bed.user = user
            bed.save()
            booking.bed = bed
            booking.status = "allotted"
            booking.save()
        return bed
    except (DatabaseError, IntegrityError):
        raise Exception("Database error during bed allocation.")
    except ObjectDoesNotExist:
        raise Exception("Required object not found.")
    except Exception:
        raise

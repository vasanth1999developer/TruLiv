import random
from django.db import models

from apps.properties.models.properties import Bed

def allocate_bed(booking, user):
    """
    Allocate a bed to the user based on availability and booking rules.
    """
    
    available_beds = Bed.objects.filter(
        property_room_type__property=booking.property,
        room_type=booking.room_type,
        is_available=True
    )
    print(available_beds)
    if not available_beds.exists():
        raise Exception("No available beds in this property and room type.")
    
    total_rooms = booking.property.related_property_room_types.filter(room_type=booking.room_type).count()
    print(total_rooms)
    total_empty_rooms = available_beds.values('property_room_type').distinct().count()
    print(total_empty_rooms)
    if total_empty_rooms == total_rooms:
        bed = available_beds.first()
        bed.is_available = False
        bed.user = user
        bed.save()
        booking.bed = bed
        booking.status = "allotted"
        booking.save()
        return bed
    vacant_rooms = (
        available_beds.values('property_room_type')
        .annotate(available_count=models.Count('id'))
        .order_by('-available_count')
    )
    if vacant_rooms.exists():
        room_id = vacant_rooms.first()['property_room_type']
        bed = available_beds.filter(property_room_type_id=room_id).first()
        bed.is_available = False
        bed.user = user
        bed.save()
        booking.bed = bed
        booking.status = "allotted"
        booking.save()
        return bed
    if available_beds.count() > 1:
        bed = random.choice(list(available_beds))
    else:
        bed = available_beds.first()
    print("hiii-------------------------------------------------------------------------------------------------------------")
   
    bed.is_available = False
    bed.user = user
    bed.save()
    booking.bed = bed
    booking.status = "allotted"
    booking.save()
    print("hiii-------------------------------------------------------------------------------------------------------------")
    return bed

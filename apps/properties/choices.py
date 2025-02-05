from djchoices import ChoiceItem, DjangoChoices


class GenderChoices(DjangoChoices):
    """Holds the choices of genders."""

    male = ChoiceItem("male", "Male")
    female = ChoiceItem("female", "Female")


class RoomTypesChoices(DjangoChoices):
    """Choices for user roles."""

    single_occupancy = ChoiceItem("single occupancy", "Single Occupancy")
    double_occupancy = ChoiceItem("double occupancy", "Double Occupancy")
    triple_occupancy = ChoiceItem("triple occupancy", "Triple Occupancy")
    quadruple_occupancy = ChoiceItem("quadruple occupancy", "Quadruple Occupancy")
    quintuple_occupancy = ChoiceItem("quintuple occupancy", "Quintuple Occupancy")
    sixtuple_occupancy = ChoiceItem("sixtuple occupancy", "Sixtuple Occupancy")


class BookingStatusChoices(DjangoChoices):
    """Choices for booking status."""

    pending = ChoiceItem("pending", "Pending")
    confirmed = ChoiceItem("confirmed", "Confirmed")
    allotted = ChoiceItem("allotted", "Bed Allotted")
    moved_in = ChoiceItem("moved_in", "Moved In")


class RoleTypeChoices(DjangoChoices):
    """Choices for user roles."""

    guest = ChoiceItem("guest", "Guest")
    customer = ChoiceItem("customer", "Customer")
    admin = ChoiceItem("admin", "Admin")


class StatusChoices(DjangoChoices):
    """Choices for payment status."""

    pending = ChoiceItem("pending", "Pending")
    paid = ChoiceItem("paid", "Paid")
    overdue = ChoiceItem("overdue", "Overdue")
    failed = ChoiceItem("failed", "Failed")

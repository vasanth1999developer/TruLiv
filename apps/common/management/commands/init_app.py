from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Initializes the app by running the necessary initial commands."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        pass

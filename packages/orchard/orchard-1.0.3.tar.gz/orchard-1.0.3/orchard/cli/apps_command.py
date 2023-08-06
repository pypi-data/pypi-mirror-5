from .command import Command
from ..api.errors import BadRequest

import logging
import sys
log = logging.getLogger(__name__)

class AppsCommand(Command):
    """
    Manage Orchard apps.

    Usage: apps COMMAND [ARGS...]

    Commands:
        ls       List apps (default)
        create   Add a new app
        rm       Remove an app

    """

    def parse(self, argv, global_options):
        if len(argv) == 0:
            argv = ['ls']

        return super(AppsCommand, self).parse(argv, global_options)

    def ls(self, options):
        """
        List apps.
        Usage: ls
        """
        apps = self.api.apps
        if apps:
            for app in apps:
                print app.name
        else:
            print "You don't have any apps yet. Run \"orchard apps create\" to create one."

    def create(self, options):
        """
        Create a new app.
        Usage: create NAME
        """
        # TODO: handle invalid or clashing app name
        try:
            app = self.api.apps.create({"name": options['NAME']})
        except BadRequest as e:
            print e.json
            sys.exit(1)
        log.info("Created %s", app.name)

    def rm(self, options):
        """
        Remove an app.
        Usage: rm NAME [NAME...]
        """
        # TODO: handle unrecognised app name
        for name in options['NAME']:
            self.api.apps[name].delete()
            log.info("Deleted %s", name)

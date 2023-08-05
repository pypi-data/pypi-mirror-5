# -*- coding: utf-8 -*-
from brightway2 import databases, methods, Database, config
from bw2data.io import EcospoldImporter, download_biosphere, \
    BW2PackageImporter, BW2PackageExporter
from bw2data.logs import upload_logs_to_server
from errors import UnknownAction, UnknownDatabase
import datetime


def strfdelta(tdelta):
    """From http://stackoverflow.com/questions/8906926/formatting-python-timedelta-objects"""
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    fmt = "{days} days {hours}h:{minutes}m:{seconds}s old"
    return fmt.format(**d)


class Controller(object):
    def dispatch(self, **kwargs):
        options = ("list", "details", "copy", "backup", "validate", "versions",
            "revert", "remove", "export", "setup", "upload_logs")
        for option in options:
            if kwargs[option]:
                return getattr(self, option)(kwargs)
        if kwargs["import"]:
            return self.importer(kwargs)
        raise UnknownAction("No suitable action found")

    def get_name(self, kwargs):
        name = kwargs['<name>']
        if name not in databases:
            raise UnknownDatabase("Can't find the database %s" % name)
        return name

    def list(self, kwargs):
        if kwargs['databases']:
            return databases.list
        else:
            return methods.list

    def details(self, kwargs):
        return databases[self.get_name(kwargs)]

    def copy(self, kwargs):
        name = self.get_name(kwargs)
        new_name = kwargs['<newname>']
        Database(name).copy(new_name)
        return u"%s copy to %s successful" % (name, new_name)

    def backup(self, kwargs):
        name = self.get_name(kwargs)
        Database(name).backup()
        return u"%s backup successful" % name

    def validate(self, kwargs):
        name = self.get_name(kwargs)
        db = Database(name)
        db.validate(db.load())
        return u"%s data validated successfully" % name

    def versions(self, kwargs):
        now = datetime.datetime.now()
        return [(x[0], x[1].strftime("Created %A, %d. %B %Y %I:%M%p"),
            strfdelta(now - x[1])) for x in Database(self.get_name(kwargs)
            ).versions()]

    def revert(self, kwargs):
        name = self.get_name(kwargs)
        revision = int(kwargs["<revision>"])
        Database(name).revert(revision)
        return u"%s reverted to revision %s" % (name, revision)

    def remove(self, kwargs):
        name = self.get_name(kwargs)
        Database(name).deregister()
        return u"%s removed" % name

    def importer(self, kwargs):
        return
        # EcospoldImporter().importer(path, name)

    def export(self, kwargs):
        name = self.get_name(kwargs)
        dependencies = kwargs["--include-dependencies"]
        path = BW2PackageExporter().export(name, dependencies)
        return u"%s exported to Brightway package: %s" % (name, path)

    def setup(self, kwargs):
        config.create_basic_directories()
        download_biosphere()
        return u"Brightway2 setup successful"

    def upload_logs(self, kwargs):
        response = upload_logs_to_server({'comment': kwargs.get('COMMENT', "")})
        if response.text == "OK":
            return "Logs uploaded successfully"
        else:
            return "There was a problem uploading the log files"

# -*- encoding: utf-8 -*-
# couchdb.py
# Copyright (C) 2013 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Classes for working with CouchDB or BigCouch instances which store email alias
maps, user UUIDs, and GPG keyIDs.
"""

from functools import partial

try:
    from paisley import client
except ImportError:
    print "This software requires paisley. Please see the README file"
    print "for instructions on getting required dependencies."

try:
    from twisted.internet import defer
    from twisted.python import log
except ImportError:
    print "This software requires Twisted. Please see the README file"
    print "for instructions on getting required dependencies."


class ConnectedCouchDB(client.CouchDB):
    """
    Connect to a CouchDB instance.

    CouchDB document for testing is '_design', and the view is simply
    a preconfigured set of mapped responses.
    """

    def __init__(self, host, port=5984, dbName=None, username=None,
                 password=None, *args, **kwargs):
        """
        Connect to a CouchDB instance.

        @param host: A hostname string for the CouchDB server.
        @type host: str
        @param port: The port of the CouchDB server.
        @type port: int
        @param dbName: (optional) The default database to bind queries to.
        @type dbName: str
        @param username: (optional) The username for authorization.
        @type username: str
        @param str password: (optional) The password for authorization.
        @type password: str
        """
        client.CouchDB.__init__(self,
                                host,
                                port=port,
                                dbName=dbName,
                                username=username,
                                password=password,
                                *args, **kwargs)

        self._cache = {}

        if dbName is None:
            databases = self.listDB()
            databases.addCallback(self._print_databases)

    def _print_databases(self, data):
        """
        Callback for listDB that prints the available databases

        @param data: response from the listDB command
        @type data: array
        """
        log.msg("Available databases:")
        for database in data:
            log.msg("  * %s" % (database,))

    def createDB(self, dbName):
        """
        Overrides ``paisley.client.CouchDB.createDB``.
        """
        pass

    def deleteDB(self, dbName):
        """
        Overrides ``paisley.client.CouchDB.deleteDB``.
        """
        pass

    def queryByLoginOrAlias(self, alias):
        """
        Check to see if a particular email or alias exists.

        @param alias: A string representing the email or alias to check.
        @type alias: str
        @return: a deferred for this query
        @rtype twisted.defer.Deferred
        """
        assert isinstance(alias, str), "Email or alias queries must be string"

        # TODO: Cache results

        d = self.openView(docId="User",
                          viewId="by_login_or_alias/",
                          key=alias,
                          reduce=False,
                          include_docs=True)

        d.addCallbacks(partial(self._get_uuid, alias), log.err)

        return d

    def _get_uuid(self, alias, result):
        """
        Parses the result of the by_login_or_alias query and gets the
        uuid

        @param alias: alias looked up
        @type alias: string
        @param result: result dictionary
        @type result: dict
        @return: The uuid for alias if available
        @rtype: str
        """
        for row in result["rows"]:
            if row["key"] == alias:
                uuid = row["id"]
                self._cache[uuid] = row["doc"].get("public_key", None)
                return uuid
        return None

    def getPubKey(self, uuid):
        pubkey = None
        try:
            pubkey = self._cache[uuid]
        except:
            pass
        return pubkey


if __name__ == "__main__":
    from twisted.internet import reactor
    cdb = ConnectedCouchDB("localhost",
                           port=6666,
                           dbName="users",
                           username="",
                           password="")

    d = cdb.queryByLoginOrAlias("test1")

    @d.addCallback
    def right(result):
        print "Should be an actual uuid:", result
        print "Public Key:"
        print cdb.getPubKey(result)

    d2 = cdb.queryByLoginOrAlias("asdjaoisdjoiqwjeoi")

    @d2.addCallback
    def wrong(result):
        print "Should be None:", result

    reactor.callLater(5, reactor.stop)
    reactor.run()

"""MongoDB UserStore implementation"""

import datetime
from pymongo import Connection
from pymongo.errors import ConnectionFailure
from pymongo.errors import OperationFailure

from pyramid.exceptions import ConfigurationError
from pyramid.decorator import reify

from osiris.store.interface import TokenStore


def includeme(config):
    settings = config.registry.settings
    host = settings.get('osiris.store.host', 'localhost')
    port = int(settings.get('osiris.store.port', '27017'))
    db = settings.get('osiris.store.db', 'osiris')
    collection = settings.get('osiris.store.collection', 'tokens')

    store = MongoDBStore(
        host=host, port=port, db=db, collection=collection,
    )
    config.registry.osiris_store = store


class MongoDBStore(TokenStore):
    """MongoDB Storage for oAuth tokens"""
    def __init__(self, host='localhost', port=27017, db="osiris",
                 collection='tokens'):
        self.host = host
        self.port = port
        self.db = db
        self.collection = collection

    @reify
    def _conn(self):
        """The MongoDB connection, cached for this call"""
        try:
            db_conn = Connection(self.host, self.port, slave_okay=False)
        except ConnectionFailure:
            raise Exception('Unable to connect to MongoDB')
        conn = db_conn[self.db]

        if not self.collection in conn.collection_names():
            conn.create_collection(self.collection)
        return conn

    def retrieve(self, **kwargs):
        query = dict([(k, v) for k, v in kwargs.items() if v])
        data = self._conn[self.collection].find_one(query)
        if data:
            return data
        else:
            return None

    def store(self, token, username, scope, expires_in):
        data = {}
        try:
            data['username'] = username
            data['token'] = token
            data['scope'] = scope
            data['issued_at'] = datetime.datetime.utcnow()
            if expires_in == '0':
                data['expire_time'] = 0
            else:
                data['expire_time'] = datetime.datetime.utcnow() + \
                    datetime.timedelta(seconds=int(expires_in))

            self._conn[self.collection].insert(data)

        except OperationFailure:
            return False
        else:
            return True

    def delete(self, token):
        try:
            self._conn[self.collection].remove({'token': token})
        except OperationFailure:
            return False
        else:
            return True

    def purge_expired(self):
        pass

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
#from sqlalchemy.dialects.postgresql import UUID
#from core import app, db

import logging
import config

Base = declarative_base()


def serialize(obj):
    import json
    if isinstance(obj.__class__, DeclarativeMeta):
        # an SQLAlchemy class
        fields = {}
        for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
            data = obj.__getattribute__(field)
            try:
                json.dumps(data) # this will fail on non-encodable values, like other classes
                fields[field] = data
            except TypeError:
                fields[field] = None
        # a json-encodable dict
        return fields


class Proxy(Base):
    """
    In SQLite, every row of every table has an 64-bit signed integer ROWID.
    The ROWID for each row is unique among all rows in the same table.

    You can access the ROWID of an SQLite table using one the special column
    names ROWID, _ROWID_, or OID. Except if you declare an ordinary table column
    to use one of those special names, then the use of that name will refer to
    the declared column not to the internal ROWID.

    See http://sqlite.org/autoinc.html for more details.

    """

    __tablename__ = 'proxy'
    __table_args__ = (UniqueConstraint('protocol', 'host', 'port'),)

    id = Column('ROWID', Integer, primary_key=True)
    protocol = Column(String(8))
    host = Column(String(255))
    port = Column(Integer)

    hit_ratio = Column(Float(precision=64)) # aggregated value
    access_time = Column(Float(precision=64)) # aggregated average value
    last_updated = Column(DateTime(timezone=True)) # aggregated average value

    def __repr__(self):
        return 'Proxy (id=%d) %s://%s:%d' % (self.id, self.protocol, self.host, self.port)

    def serialize(self):
        return serialize(self)

    def test_reference_page(self, timeout=config.DEFAULT_TIMEOUT):
        """Tests if the proxy server returns an HTTP 200 message and a correct content
        when trying to access a reference page."""

        import random
        import requests

        proxy_dict = {'http': '%s:%d' % (self.host, self.port)}
        random_key = random.randint(0, 100000000)
        url = 'http://static.suminb.com/ref.php?key=%d' % random_key

        try:
            r = requests.get(url, proxies=proxy_dict, timeout=timeout)

            if r.status_code == 200 and r.text.strip() == str(random_key):
                return True

        except Exception as e:
            logging.error(e)

        return False

    def test_nonexisting_page(self, timeout=config.DEFAULT_TIMEOUT):
        """Tests if the proxy server returns an HTTP 404 message when trying to access a
        non-existing page."""

        import requests

        proxy_dict = {'http': '%s:%d' % (self.host, self.port)}
        url = 'http://static.suminb.com/nonexisting'

        try:
            r = requests.get(url, proxies=proxy_dict, timeout=timeout)

            if r.status_code == 404:
                return True

        except Exception as e:
            logging.error(e)

        return False

    def test_nonexisting_domain(self, timeout=config.DEFAULT_TIMEOUT):
        """Tests if the proxy server times-out when trying to access a non-existing domain."""

        import requests

        proxy_dict = {'http': '%s:%d' % (self.host, self.port)}
        url = 'http://nonexisting.suminb.com'

        try:
            r = requests.get(url, proxies=proxy_dict, timeout=timeout)

            # Should not reach here unless the proxy is lying.
            return False

        except Exception as e:
            logging.error(e)

        return True

    def fetch_url(self, url, headers=[], params=[]):

        from datetime import datetime
        import time
        import requests
        import proxybank

        proxy_dict = {self.protocol: '%s:%d' % (self.host, self.port)}
        alive = False
        status_code = None

        start_time = time.time()

        try:
            # TODO: Support for other HTTP verbs
            req = requests.get(url, headers=headers, proxies=proxy_dict, timeout=proxybank.config.DEFAULT_TIMEOUT)
            alive = True
            status_code = req.status_code

        except ConnectionError as e:
            logging.error(e)

        except Timeout as e:
            logging.error(e)

        end_time = time.time()

        record = AccessRecord(
            proxy_id=self.id,
            timestamp=datetime.now(),
            alive=alive,
            url=url,
            access_time=end_time-start_time,
            status_code=status_code)

        db.session.add(record)
        db.session.commit()

        return req

class AccessRecord(Base):
    __tablename__ = 'access_record'

    id = Column('ROWID', Integer, primary_key=True)
    proxy_id = Column(Integer)
    timestamp = Column(DateTime(timezone=True))

    user_agent = Column(String(255))
    remote_address = Column(String(64))
    
    alive = Column(Boolean)
    url = Column(String(255))
    status_code = Column(Integer)
    access_time = Column(Float(precision=64))

    def serialize(self):
        return serialize(self)

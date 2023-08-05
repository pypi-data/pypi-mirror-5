from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from wtforms_test import FormTestCase


class MultiDict(dict):
    def getlist(self, key):
        return [self[key]]


class DatabaseTestCase(FormTestCase):
    def setup_method(self, method):
        self.engine = create_engine('sqlite:///:memory:')

        self.base = declarative_base()
        self.create_models()

        self.base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        self.session.close_all()
        self.base.metadata.drop_all(self.engine)
        self.engine.dispose()

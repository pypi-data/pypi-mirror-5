# -*- coding: utf-8 -*-
import sqlalchemy as sa

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import (
    make_searchable, SearchQueryMixin, search_manager
)


make_searchable()


class TestCase(object):
    def setup_method(self, method):
        self.engine = create_engine(
            'postgres://postgres@localhost/sqlalchemy_searchable_test'
        )
        self.Base = declarative_base()
        self.create_models()
        self.Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        self.session.close_all()
        self.Base.metadata.drop_all(self.engine)
        search_manager.processed_columns = []

    def create_models(self):
        class TextItemQuery(Query, SearchQueryMixin):
            pass

        class TextItem(self.Base):
            __tablename__ = 'textitem'

            id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

            name = sa.Column(sa.Unicode(255))

            search_vector = sa.Column(TSVectorType('name', 'content'))

            content = sa.Column(sa.UnicodeText)

        class Order(self.Base):
            __tablename__ = 'order'
            id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
            name = sa.Column(sa.Unicode(255))
            search_vector = sa.Column(TSVectorType('name'))

        class Article(TextItem):
            __tablename__ = 'article'
            id = sa.Column(
                sa.Integer, sa.ForeignKey(TextItem.id), primary_key=True
            )

            created_at = sa.Column(sa.DateTime)

        self.TextItemQuery = TextItemQuery
        self.TextItem = TextItem
        self.Order = Order
        self.Article = Article


class SchemaTestCase(TestCase):
    should_create_indexes = []
    should_create_triggers = []

    def test_creates_search_index(self):
        rows = self.session.execute(
            """SELECT relname
            FROM pg_class
            WHERE oid IN (
                SELECT indexrelid
                FROM pg_index, pg_class
                WHERE pg_class.relname='textitem'
                    AND pg_class.oid=pg_index.indrelid
                    AND indisunique != 't'
                    AND indisprimary != 't'
            ) ORDER BY relname"""
        ).fetchall()
        assert self.should_create_indexes == map(lambda a: a[0], rows)

    def test_creates_search_trigger(self):
        rows = self.session.execute(
            """SELECT DISTINCT trigger_name
            FROM information_schema.triggers
            WHERE event_object_table = 'textitem'
            AND trigger_schema NOT IN
                ('pg_catalog', 'information_schema')
            ORDER BY trigger_name"""
        ).fetchall()
        print rows
        assert self.should_create_triggers == map(lambda a: a[0], rows)

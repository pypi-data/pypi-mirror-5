# import sqlalchemy as sa
# from sqlalchemy_utils import TSVectorType
# from tests import Base


# class TextItem(Base):
#     __search_options__ = {
#         'tablename': 'textitem',
#         'search_vector_name': 'search_vector',
#         'search_trigger_name': '{table}_search_update',
#         'search_index_name': '{table}_search_index',
#     }
#     __tablename__ = 'textitem'

#     id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

#     name = sa.Column(sa.Unicode(255))

#     search_vector = sa.Column(TSVectorType('name', 'content'))

#     content = sa.Column(sa.UnicodeText)


# class Order(Base):
#     __tablename__ = 'order'
#     id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
#     name = sa.Column(sa.Unicode(255))
#     search_vector = sa.Column(TSVectorType('name'))


# class Article(TextItem):
#     __tablename__ = 'article'
#     id = sa.Column(sa.Integer, sa.ForeignKey(TextItem.id), primary_key=True)

#     created_at = sa.Column(sa.DateTime)

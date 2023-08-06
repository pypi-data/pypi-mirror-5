import sqlalchemy as sa
from sqlalchemy_utils import batch_fetch
from tests import TestCase


class TestBatchFetchManyToOneRelationships(TestCase):
    def create_models(self):
        class User(self.Base):
            __tablename__ = 'user'
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255))

        class Article(self.Base):
            __tablename__ = 'article'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255))
            author_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))

            author = sa.orm.relationship(
                User,
                backref=sa.orm.backref(
                    'articles'
                )
            )

        self.User = User
        self.Article = Article

    def setup_method(self, method):
        TestCase.setup_method(self, method)
        articles = [
            self.Article(name=u'Article 1', author=self.User(name=u'John')),
            self.Article(name=u'Article 2', author=self.User(name=u'Matt')),
        ]
        self.session.add_all(articles)
        self.session.commit()

    def test_supports_relationship_attributes(self):
        articles = self.session.query(self.Article).all()
        batch_fetch(
            articles,
            'author'
        )
        query_count = self.connection.query_count
        assert articles[0].author  # no lazy load should occur
        assert articles[1].author  # no lazy load should occur
        assert self.connection.query_count == query_count

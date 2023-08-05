import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_i18n import Translatable, configure_translatables


class TestCase(object):
    def setup_method(self, method):
        self.engine = create_engine(
            'postgres://postgres@localhost/sqlalchemy_i18n_test'
        )
        self.Model = declarative_base()

        self.create_models()

        sa.event.listen(
            sa.orm.mapper, 'after_configured', configure_translatables
        )

        sa.orm.configure_mappers()
        self.Model.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        self.session.close_all()
        self.Model.metadata.drop_all(self.engine)
        self.engine.dispose()

    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText)
            ]
            __translatable__ = {
                'locale_getter': lambda: 'en',
                'base_classes': (self.Model, )
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)

        self.Article = Article

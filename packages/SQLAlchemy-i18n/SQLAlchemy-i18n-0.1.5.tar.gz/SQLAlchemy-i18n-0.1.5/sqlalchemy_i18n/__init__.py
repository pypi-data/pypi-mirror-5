from copy import copy
import inspect
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property, Comparator


class ProxyDict(object):
    def __init__(self, parent, collection_name, child_class, key_name):
        self.parent = parent
        self.collection_name = collection_name
        self.child_class = child_class
        self.key_name = key_name
        self.cache = {}

    @property
    def collection(self):
        return getattr(self.parent, self.collection_name)

    def keys(self):
        descriptor = getattr(self.child_class, self.key_name)
        return [x[0] for x in self.collection.values(descriptor)]

    def __contains__(self, key):
        try:
            return key in self.cache or self[key]
        except KeyError:
            return False

    def fetch(self, key):
        return self.collection.filter_by(**{self.key_name: key}).first()

    def __getitem__(self, key):
        if key in self.cache:
            return self.cache[key]

        session = sa.orm.object_session(self.parent)
        if not session or not sa.orm.util.has_identity(self.parent):
            value = self.child_class(**{self.key_name: key})
            self.collection.append(value)
        else:
            value = self.fetch(key)
            if not value:
                value = self.child_class(**{self.key_name: key})
                self.collection.append(value)

        self.cache[key] = value
        return value

    def __setitem__(self, key, value):
        try:
            existing = self[key]
            self.collection.remove(existing)
        except KeyError:
            pass
        self.collection.append(value)
        self.cache[key] = value


def remove_property(class_, name):
    mapper = class_.mapper
    table = class_.__table__
    columns = class_.mapper.c
    column = columns[name]
    del columns._data[name]
    del mapper.columns[name]
    columns._all_cols.remove(column)
    mapper._cols_by_table[table].remove(column)
    mapper.class_manager.uninstrument_attribute(name)
    del mapper._props[name]


def primary_keys(model):
    for column in model.__table__.c:
        if column.primary_key:
            yield column


class Translatable(object):
    __translatable__ = {}

    @hybrid_property
    def current_translation(self):
        locale = self.__translatable__['locale_getter']()
        if locale in self.translations:
            return self.translations[locale]

        class_ = self.__translatable__['class']
        obj = class_()
        obj.locale = locale
        self.translations[locale] = obj
        return obj

    @current_translation.expression
    def current_translation(cls):
        try:
            return cls._current_translation
        except AttributeError:
            locale = cls.__translatable__['locale_getter']()
            translation_cls = cls.__translatable__['class']
            cls._current_translation = sa.orm.relationship(
                translation_cls,
                primaryjoin=sa.and_(
                    cls.id == translation_cls.id,
                    translation_cls.locale == locale
                ),
                uselist=False,
                cascade='all, delete-orphan',
                passive_deletes=True,
            )
            return cls._current_translation

    @property
    def translations(self):
        try:
            return self.proxied_translations
        except AttributeError:
            self.proxied_translations = ProxyDict(
                self,
                '_translations',
                self.__translatable__['class'],
                'locale'
            )
        return self.proxied_translations

    @classmethod
    def __declare_last__(cls):
        generator = TranslationModelGenerator(cls)
        generator()


def translation_getter_factory(name):
    return lambda self: getattr(self.current_translation, name)


def translation_setter_factory(name):
    return (
        lambda self, value:
        setattr(self.current_translation, name, value)
    )


class TranslationTransformer(Comparator):
    def __init__(self, cls):
        self.alias = sa.orm.aliased(cls.__translatable__['class'])
        self.parent = cls

    @property
    def join(self):
        def go(q):
            return q.outerjoin(self.alias, self.parent.current_translation)
        return go

    def operate(self, op, other):
        return op(self.alias.name, other)


class TranslationModelGenerator(object):
    DEFAULT_OPTIONS = {
        'table_name': '%s_translation',
        'locale_column_name': 'locale',
        'base_classes': None
    }

    def __init__(self, model):
        self.model = model
        parents = inspect.getmro(self.model)
        self.translation_class = None
        for parent in parents:
            try:
                self.translation_class = parent.__translatable__['class']
            except AttributeError:
                pass
            except KeyError:
                pass

    @property
    def table_name(self):
        if self.translation_class:
            return self.translation_class.__table__.name
        return self.option('table_name') % self.model.__tablename__

    def option(self, name):
        try:
            return self.model.__translatable__[name]
        except (AttributeError, KeyError):
            return self.DEFAULT_OPTIONS[name]

    def build_reflected_primary_keys(self):
        columns = []
        for column in primary_keys(self.model):
            columns.append(
                sa.Column(
                    column.name,
                    column.type,
                    primary_key=True
                )
            )
        return columns

    def build_foreign_key(self):
        names = [column.name for column in primary_keys(self.model)]
        return sa.schema.ForeignKeyConstraint(
            names,
            [
                '%s.%s' % (self.model.__tablename__, name)
                for name in names
            ],
            ondelete='CASCADE'
        )

    def build_locale_column(self):
        return sa.Column(
            self.option('locale_column_name'),
            sa.String(10),
            primary_key=True
        )

    def build_columns(self):
        columns = self.build_reflected_primary_keys()
        columns.append(self.build_locale_column())
        columns.extend(self.model.__translated_columns__)
        return columns

    def build_table(self):
        table_exists = self.table_name in self.model.metadata.tables
        items = self.build_columns()
        if table_exists:
            table = self.model.metadata.tables[self.table_name]
            for column in table.c:
                for c in items:
                    if c.name == column.name:
                        items.remove(c)
        else:
            items.append(self.build_foreign_key())

        return sa.schema.Table(
            self.table_name,
            self.model.__bases__[0].metadata,
            *items,
            extend_existing=table_exists
        )

    def assign_attr_getter_setters(self, attr):
        setattr(
            self.model,
            attr,
            hybrid_property(
                fget=translation_getter_factory(attr),
                fset=translation_setter_factory(attr),
                expr=lambda cls: getattr(self.translation_class, attr)
            )
        )

    def build_getters_and_setters(self):
        for column in self.model.__translated_columns__:
            self.assign_attr_getter_setters(column.name)

    def build_relationship(self):
        self.model._translations = sa.orm.relationship(
            self.translation_class,
            lazy='dynamic',
            cascade='all, delete-orphan',
            passive_deletes=True,
            backref=sa.orm.backref('parent'),
        )

    def build_model(self):
        if not self.option('base_classes'):
            raise Exception(
                'Missing __translatable__ base_classes option for model %s.'
                % self.model.__name__
            )
        return type(
            '%sTranslation' % self.model.__name__,
            self.option('base_classes'),
            {'__table__': self.build_table()}
        )

    def __call__(self):
        # translatable attributes need to be copied for each child class,
        # otherwise each child class would share the same __translatable__
        # option dict
        self.model.__translatable__ = copy(self.model.__translatable__)
        if not self.translation_class:
            self.translation_class = self.build_model()
            self.build_relationship()
        else:
            self.translation_class.__table__ = self.build_table()
        self.model.__translatable__['class'] = self.translation_class
        self.translation_class.__parent_class__ = self.model
        self.build_getters_and_setters()

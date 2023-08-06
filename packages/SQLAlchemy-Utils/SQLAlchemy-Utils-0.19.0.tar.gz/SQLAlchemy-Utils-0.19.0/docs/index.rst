.. SQLAlchemy-Utils documentation master file, created by
   sphinx-quickstart on Tue Feb 19 11:16:09 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SQLAlchemy-Utils
================

SQLAlchemy-Utils provides custom data types and various utility functions for SQLAlchemy.

Using automatic data coercion
-----------------------------

SQLAlchemy-Utils provides various new data types for SQLAlchemy and in order to gain full
advantage of these datatypes you should use coercion_listener. Setting up the listener is easy:

::

    import sqlalchemy as sa
    from sqlalchemy_utils import coercion_listener


    sa.event.listen(sa.orm.mapper, 'mapper_configured', coercion_listener)


The listener automatically detects SQLAlchemy-Utils compatible data types and coerces all attributes
using these types to appropriate objects.


Example
::


    from colour import Color
    from sqlalchemy_utils import ColorType


    class Document(Base):
        __tablename__ = 'player'
        id = sa.Column(sa.Integer, autoincrement=True)
        name = sa.Column(sa.Unicode(50))
        background_color = sa.Column(ColorType)


    document = Document()
    document.background_color = 'F5F5F5'
    document.background_color  # Color object
    session.commit()



Data types
----------

SQLAlchemy-Utils provides various new data types for SQLAlchemy.


ChoiceType
^^^^^^^^^^

ChoiceType offers way of having fixed set of choices for given column. Columns with ChoiceTypes are automatically coerced to Choice objects.


::


    class User(self.Base):
        TYPES = [
            (u'admin', u'Admin'),
            (u'regular-user', u'Regular user')
        ]

        __tablename__ = 'user'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(255))
        type = sa.Column(ChoiceType(TYPES))


    user = User(type=u'admin')
    user.type  # Choice(type='admin', value=u'Admin')



ChoiceType is very useful when the rendered values change based on user's locale:

::

    from babel import lazy_gettext as _


    class User(self.Base):
        TYPES = [
            (u'admin', _(u'Admin')),
            (u'regular-user', _(u'Regular user'))
        ]

        __tablename__ = 'user'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(255))
        type = sa.Column(ChoiceType(TYPES))


    user = User(type=u'admin')
    user.type  # Choice(type='admin', value=u'Admin')

    print user.type  # u'Admin'


ColorType
^^^^^^^^^

ColorType provides a way for saving Color (from colour_ package) objects into database.
ColorType saves Color objects as strings on the way in and converts them back to objects when querying the database.

::


    from colour import Color
    from sqlalchemy_utils import ColorType


    class Document(Base):
        __tablename__ = 'document'
        id = sa.Column(sa.Integer, autoincrement=True)
        name = sa.Column(sa.Unicode(50))
        background_color = sa.Column(ColorType)


    document = Document()
    document.background_color = Color('#F5F5F5')
    session.commit()


Querying the database returns Color objects:

::

    document = session.query(Document).first()

    document.background_color.hex
    # '#f5f5f5'


For more information about colour package and Color object, see https://github.com/vaab/colour


LocaleType
^^^^^^^^^^

LocaleType saves Babel_ Locale objects into database. The Locale objects are converted to string on the way in and back to object on the way out.

In order to use LocaleType you need to install Babel_ first.


::


    from sqlalchemy_utils import LocaleType
    from babel import Locale


    class User(Base):
        __tablename__ = 'user'
        id = sa.Column(sa.Integer, autoincrement=True)
        name = sa.Column(sa.Unicode(50))
        locale = sa.Column(LocaleType)


    user = User()
    user.locale = Locale('en_US')
    session.commit()


Like many other types this type also supports scalar coercion:

::


    user.locale = 'de_DE'
    user.locale  # Locale('de_DE')



NumberRangeType
^^^^^^^^^^^^^^^

NumberRangeType provides way for saving range of numbers into database.

Example ::


    from sqlalchemy_utils import NumberRangeType, NumberRange


    class Event(Base):
        __tablename__ = 'user'
        id = sa.Column(sa.Integer, autoincrement=True)
        name = sa.Column(sa.Unicode(255))
        estimated_number_of_persons = sa.Column(NumberRangeType)


    party = Event(name=u'party')

    # we estimate the party to contain minium of 10 persons and at max
    # 100 persons
    party.estimated_number_of_persons = NumberRange(10, 100)

    print party.estimated_number_of_persons
    # '10-100'


NumberRange supports some arithmetic operators:
::


    meeting = Event(name=u'meeting')

    meeting.estimated_number_of_persons = NumberRange(20, 40)

    total = (
        meeting.estimated_number_of_persons +
        party.estimated_number_of_persons
    )
    print total
    # '30-140'



ScalarListType
^^^^^^^^^^^^^^

ScalarListType type provides convenient way for saving multiple scalar values in one
column. ScalarListType works like list on python side and saves the result as comma-separated list
in the database (custom separators can also be used).

Example ::


    from sqlalchemy_utils import ScalarListType


    class User(Base):
        __tablename__ = 'user'
        id = sa.Column(sa.Integer, autoincrement=True)
        hobbies = sa.Column(ScalarListType())


    user = User()
    user.hobbies = [u'football', u'ice_hockey']
    session.commit()


You can easily set up integer lists too:

::


    from sqlalchemy_utils import ScalarListType


    class Player(Base):
        __tablename__ = 'player'
        id = sa.Column(sa.Integer, autoincrement=True)
        points = sa.Column(ScalarListType(int))


    player = Player()
    player.points = [11, 12, 8, 80]
    session.commit()



URLType
^^^^^^^

URLType stores furl_ objects into database.

::

    from sqlalchemy_utils import URLType
    from furl import furl


    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.Integer, primary_key=True)
        website = sa.Column(URLType)


    user = User(website=u'www.example.com')

    # website is coerced to furl object, hence all nice furl operations come
    # available
    user.website.args['some_argument'] = '12'

    print user.website
    # www.example.com?some_argument=12



UUIDType
^^^^^^^^

UUIDType will store a UUID in the database in a native format, if available,
or a 16-byte BINARY column or a 32-character CHAR column if not.

::

    from sqlalchemy_utils import UUIDType
    import uuid

    class User(Base):
        __tablename__ = 'user'

        # Pass `binary=False` to fallback to CHAR instead of BINARY
        id = sa.Column(UUIDType(binary=False), primary_key=True)


TimezoneType
^^^^^^^^^^^^

TimezoneType provides a way for saving timezones (from either the pytz or the dateutil package) objects into database.
TimezoneType saves timezone objects as strings on the way in and converts them back to objects when querying the database.


::

    from sqlalchemy_utils import UUIDType

    class User(Base):
        __tablename__ = 'user'

        # Pass backend='pytz' to change it to use pytz (dateutil by default)
        timezone = sa.Column(TimezoneType(backend='pytz'))


The generates decorator
-----------------------

Many times you may have generated property values. Usual cases include slugs from names or resized thumbnails from images.

SQLAlchemy-Utils provides a way to do this easily with `generates` decorator:

::


    class Article(self.Base):
        __tablename__ = 'article'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(255))
        slug = sa.Column(sa.Unicode(255))

        @generates(slug)
        def _create_slug(self):
            return self.name.lower().replace(' ', '-')


    article = self.Article()
    article.name = u'some article name'
    self.session.add(article)
    self.session.flush()
    assert article.slug == u'some-article-name'


You can also pass the attribute name as a string argument for `generates`:

::

    class Article(self.Base):
        ...

        @generates('slug')
        def _create_slug(self):
            return self.name.lower().replace(' ', '-')


These property generators can even be defined outside classes:

::


    class Article(self.Base):
        __tablename__ = 'article'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(255))
        slug = sa.Column(sa.Unicode(255))


    @generates(Article.slug)
    def _create_article_slug(self):
        return self.name.lower().replace(' ', '-')


Or with lazy evaluated string argument:

::


    @generates('Article.slug')
    def _create_article_slug(self):
        return self.name.lower().replace(' ', '-')


Generic Relationship
--------------------

Generic relationship is a form of relationship that supports creating a 1 to many relationship to any target model.

::

    from sqlalchemy_utils import generic_relationship

    class User(Base):
        __tablename__ = 'user'
        id = sa.Column(sa.Integer, primary_key=True)

    class Customer(Base):
        __tablename__ = 'customer'
        id = sa.Column(sa.Integer, primary_key=True)

    class Event(Base):
        __tablename__ = 'event'
        id = sa.Column(sa.Integer, primary_key=True)

        # This is used to discriminate between the linked tables.
        object_type = sa.Column(sa.Unicode(255))

        # This is used to point to the primary key of the linked row.
        object_id = sa.Column(sa.Integer)

        object = generic_relationship(object_type, object_id)


    # Some general usage to attach an event to a user.
    us_1 = User()
    cu_1 = Customer()

    session.add_all([us_1, cu_1])
    session.commit()

    ev = Event()
    ev.object = us_1

    session.add(ev)
    session.commit()

    # Find the event we just made.
    session.query(Event).filter_by(object=us_1).first()

    # Find any events that are bound to users.
    session.query(Event).filter(Event.object.is_type(User)).all()



.. _Babel: http://babel.pocoo.org/
.. _furl: https://github.com/gruns/furl
.. _colour: https://github.com/vaab/colour


API Documentation
-----------------

.. module:: sqlalchemy_utils

.. autoclass:: InstrumentedList
    :members:


.. module:: sqlalchemy_utils.functions

.. autofunction:: sort_query
.. autofunction:: escape_like
.. autofunction:: naturally_equivalent
.. autofunction:: has_changes
.. autofunction:: non_indexed_foreign_keys
.. autofunction:: is_indexed_foreign_key
.. autofunction:: identity
.. autofunction:: is_auto_assigned_date_column
.. autofunction:: declarative_base


.. include:: ../CHANGES.rst


License
-------

.. include:: ../LICENSE

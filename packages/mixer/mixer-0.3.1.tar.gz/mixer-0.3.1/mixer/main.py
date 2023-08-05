# coding: utf-8
"""
    mixer.main
    ~~~~~~~~~~

    This module implements the objects generation.

    :copyright: 2013 by Kirill Klenov.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
from copy import deepcopy

import decimal
from importlib import import_module
from collections import defaultdict
from types import GeneratorType

from . import generators as g, fakers as f, mix_types as t
from . import six


DEFAULT = object()
RANDOM = object()
FAKE = object()
SELECT = object()


class Field(object):
    """ Store field imformation.
    """
    is_relation = False

    def __init__(self, scheme, name):
        self.scheme = scheme
        self.name = name

    def __deepcopy__(self, memo):
        return Field(self.scheme, self.name)


class Relation(Field):
    """ Store relation field information.
    """
    is_relation = True

    def __init__(self, scheme, name, params=None):
        super(Relation, self).__init__(scheme, name)
        self.params = params or dict()

    def __deepcopy__(self, memo):
        return Relation(self.scheme, self.name, deepcopy(self.params))


class Mix(object):
    """ Saves a chain of attirbutes for feature usage.

        ::

            t =  Mix()
            t.one.two
            t & obj  # equal: getattr(getattr(obj, 'one'), 'two')
    """
    def __init__(self, value=None, parent=None):
        self.__value = value
        self.__parent = parent
        self.__func = None

    def __getattr__(self, value):
        return Mix(value, self if self.__value else None)

    def __call__(self, func):
        self.__func = func
        return self

    def __and__(self, value):
        if self.__parent:
            value = self.__parent & value
        value = getattr(value, self.__value)
        if self.__func:
            return self.__func(value)
        return value

    def __str__(self):
        return '%s/%s' % (self.__value, str(self.__parent or ''))

    def __repr__(self):
        return '<Mix %s>' % str(self)


class GeneratorMeta(type):
    """ Precache generators.
    """
    def __new__(mcs, name, bases, params):
        generators = dict()
        fakers = dict()
        types = dict()

        for cls in bases:
            if isinstance(cls, GeneratorMeta):
                generators.update(cls.generators)
                fakers.update(cls.fakers)
                types.update(cls.types)

        generators.update(params.get('generators', dict()))
        fakers.update(params.get('fakers', dict()))
        types.update(params.get('types', dict()))

        generators = dict(mcs.flat_keys(generators))
        types = dict(mcs.flat_keys(types))

        params['generators'] = generators
        params['fakers'] = fakers
        params['types'] = types

        return super(GeneratorMeta, mcs).__new__(mcs, name, bases, params)

    @staticmethod
    def flat_keys(d):
        for key, value in d.items():
            if isinstance(key, (tuple, list)):
                for k in key:
                    yield k, value
                continue
            yield key, value


class Generator(six.with_metaclass(GeneratorMeta)):
    """ Make generators for types.
    """
    generators = {
        bool: g.gen_boolean,
        float: g.gen_float,
        int: g.gen_integer,
        str: g.gen_string,
        datetime.date: g.gen_date,
        datetime.datetime: g.gen_datetime,
        datetime.time: g.gen_time,
        decimal.Decimal: g.gen_decimal,
        t.BigInteger: g.gen_big_integer,
        t.EmailString: f.gen_email,
        t.HostnameString: f.gen_hostname,
        t.IP4String: f.gen_ip4,
        t.NullOrBoolean: g.gen_null_or_boolean,
        t.PositiveDecimal: g.gen_positive_decimal,
        t.PositiveInteger: g.gen_positive_integer,
        t.SmallInteger: g.gen_small_integer,
        t.Text: f.gen_lorem,
        None: g.loop(lambda: ''),
    }

    fakers = {
        ('name', str): f.gen_name,
        ('first_name', str): f.gen_firstname,
        ('firstname', str): f.gen_firstname,
        ('last_name', str): f.gen_lastname,
        ('lastname', str): f.gen_lastname,
        ('title', str): f.gen_lorem,
        ('description', str): f.gen_lorem,
        ('content', str): f.gen_lorem,
        ('body', str): f.gen_lorem,
        ('city', str): f.gen_city,
        ('country', str): f.gen_country,
        ('email', str): f.gen_email,
        ('username', str): f.gen_username,
        ('login', str): f.gen_username,
        ('domain', str): f.gen_hostname,
    }

    types = {}

    @classmethod
    def cls_to_simple(cls, fcls):
        """ Translate class to one of simple base types.
        """
        return cls.types.get(fcls) or (
            fcls if fcls in cls.generators
            else None
        )

    @staticmethod
    def name_to_simple(fname):
        """ Translate name to one of simple base names.
        """
        fname = fname or ''
        return fname.lower().strip()

    @classmethod
    def gen_maker(cls, fcls, fname=None, fake=False):
        """ Generate value based on class and name.
        """
        fcls = cls.cls_to_simple(fcls)
        fname = cls.name_to_simple(fname)

        gen_maker = cls.generators.get(fcls)

        if fname and fake and (fname, fcls) in cls.fakers:
            gen_maker = cls.fakers.get((fname, fcls)) or gen_maker

        return gen_maker


class TypeMixerMeta(type):
    """ Cache mixers by class.
    """
    mixers = dict()

    def __call__(cls, cls_type, mixer=None, generator=None, fake=True):
        cls_type = cls.__load_cls(cls_type)
        key = (mixer, cls_type, fake, generator)
        if not key in cls.mixers:
            cls.mixers[key] = super(TypeMixerMeta, cls).__call__(
                cls_type, mixer=mixer, generator=generator, fake=fake,
            )
        return cls.mixers[key]

    @staticmethod
    def __load_cls(cls_type):
        if isinstance(cls_type, six.string_types):
            mod, cls_type = cls_type.rsplit('.', 1)
            mod = import_module(mod)
            cls_type = getattr(mod, cls_type)
        return cls_type


class TypeMixer(six.with_metaclass(TypeMixerMeta)):

    fake = FAKE
    generator = Generator
    select = SELECT
    random = RANDOM

    def __init__(self, cls, mixer=None, generator=None, fake=True):
        self.cls = cls
        self.mixer = mixer
        self.fake = fake
        self.fields = dict(self.__load_fields())
        self.generator = generator or self.generator
        self.generators = dict()
        self.gen_values = defaultdict(set)

    def __repr__(self):
        return "<TypeMixer {0}>".format(self.cls)

    def blend(self, **values):
        """
        Generate instance.

        :param **values: Predefined fields
        """
        target = self.cls()

        defaults = deepcopy(self.fields)

        # Prepare relations
        for key, params in values.items():
            if '__' in key:
                rname, rvalue = key.split('__', 1)
                field = defaults.get(rname)
                if not isinstance(field, Relation):
                    defaults[rname] = Relation(
                        field and field.scheme or field,
                        field and field.name or rname)
                defaults[rname].params.update({rvalue: params})
                continue
            defaults[key] = params

        # Fill fields
        post_values = filter(None, (
            self.set_value(target, fname, fvalue, finaly=True)
            for (fname, fvalue) in filter(None, self.fill_fields(
                target, defaults
            ))
        ))

        if self.mixer:
            target = self.mixer.post_generate(target)

        for fname, fvalue in post_values:
            setattr(target, fname, fvalue)

        return target

    def fill_fields(self, target, defaults):

        for fname, fvalue in defaults.items():

            if isinstance(fvalue, Relation):
                yield self.gen_relation(target, fname, fvalue)
                continue

            if isinstance(fvalue, Field):
                yield self.gen_field(target, fname, fvalue)
                continue

            if fvalue is self.random:
                yield self.gen_random(target, fname)
                continue

            if fvalue is self.fake:
                yield self.gen_fake(target, fname)
                continue

            if fvalue is self.select:
                yield self.gen_select(target, fname)
                continue

            yield self.set_value(target, fname, fvalue)

    def set_value(self, target, field_name, field_value, finaly=False):
        """ Set `value` to `target` as `field_name`.
        """
        if isinstance(field_value, Mix):
            if not finaly:
                return field_name, field_value

            return self.set_value(
                target, field_name, field_value & target, finaly=finaly)

        if callable(field_value):
            return self.set_value(
                target, field_name, field_value(), finaly=finaly)

        if isinstance(field_value, GeneratorType):
            return self.set_value(
                target, field_name, next(field_value), finaly=finaly)

        setattr(target, field_name, field_value)

    def gen_value(self, target, field_name, field_class, fake=None,
                  unique=False):
        """ Generate values from basic types.
            Set value to target.
        """
        fake = self.fake if fake is None else fake
        gen = self.get_generator(field_class, field_name, fake=fake)
        value = next(gen)

        if unique:
            counter = 0
            while value in self.gen_values[field_class]:
                value = next(gen)
                counter += 1
                if counter > 100:
                    raise RuntimeError(
                        "Cannot generate a unique value for %s" % field_name
                    )
            self.gen_values[field_class].add(value)

        return self.set_value(target, field_name, value)

    def gen_field(self, target, field_name, field):
        """
        Generate value by field.

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        :param relation: Instance of :class:`Field`
        """
        unique = self.is_unique(field)
        return self.gen_value(target, field_name, field.scheme, unique=unique)

    def gen_relation(self, target, field_name, relation):
        """
        Generate a related field by `relation`

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        :param relation: Instance of :class:`Relation`

        """
        mixer = TypeMixer(relation.scheme, self.mixer, self.generator)
        return self.set_value(
            target, field_name, mixer.blend(**relation.params))

    def gen_random(self, target, field_name):
        """
        Generate random value of field with `field_name` for `target`

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        """
        field = self.fields.get(field_name)
        scheme = field and field.scheme or field
        return self.gen_value(target, field_name, scheme, fake=False)

    gen_select = gen_random

    def gen_fake(self, target, field_name):
        """
        Generate fake value of field with `field_name` for `target`

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        """
        field = self.fields.get(field_name)
        return self.gen_value(target, field_name, field.scheme, fake=True)

    def get_generator(self, field_class, field_name=None, fake=None):
        """
        Cache generator for class.

        :param field_class: Class for looking a generator
        :param field_name: Name of field for generation
        :param fake: Generate fake data instead of random data.
        """
        if fake is None:
            fake = self.fake

        key = (field_class, field_name, fake)

        if not key in self.generators:
            self.generators[key] = self.make_generator(
                field_class, field_name, fake)

        return self.generators[key]

    def make_generator(self, field_class, field_name=None, fake=None):
        """
        Make generator for class.

        :param field_class: Class for looking a generator
        :param field_name: Name of field for generation
        :param fake: Generate fake data instead of random data.
        """
        return self.generator.gen_maker(field_class, field_name, fake)()

    @staticmethod
    def is_unique(field):
        """ Return True is field's value should be a unique.
        """
        return False

    def __load_fields(self):
        """ Generator of scheme's fields.
        """
        for fname in dir(self.cls):
            if fname.startswith('_'):
                continue
            yield fname, Field(getattr(self.cls, fname), fname)


class MetaMixer:

    def __init__(self, mixer, count=5):
        self.count = count
        self.mixer = mixer

    def blend(self, scheme, **values):
        result = []
        for _ in range(self.count):
            result.append(
                self.mixer.blend(scheme, **values)
            )
        return result

    def __getattr__(self, name):
        raise AttributeError('Use "cycle" only for "blend"')


class Mixer(object):
    """
    This class is used for integration to one or more applications.

    :param fake: (True) Generate fake data instead of random data.
    :param generator: (:class:`~mixer.main.Generator`) A class for
                        generation values for types

    ::

        class SomeScheme:
            score = int
            name = str

        mixer = Mixer()
        instance = mixer.blend(SomeScheme)
        print instance.name  # Some like: 'Mike Douglass'

        mixer = Mixer(fake=False)
        instance = mixer.blend(SomeScheme)
        print instance.name  # Some like: 'AKJfdjh3'

    """

    #: Force `fake` value
    #: If you initialized a :class:`Mixer` with `fake=False`
    #: you can force a `fake` value for field with this attribute
    #: ::
    #:
    #:      mixer = Mixer(fake=False)
    #:      user = mixer.blend(User)
    #:      print user.name  # Some like: Fdjw4das
    #:      user = mixer.blend(User, name=mixer.fake)
    #:      print user.name  # Some like: Bob Marley
    fake = FAKE

    #: Force `random` value
    #: If you initialized a :class:`Mixer` with `fake=True` by default
    #: you can force a `random` value for field with this attribute
    #: ::
    #:
    #:      mixer = Mixer()
    #:      user = mixer.blend(User)
    #:      print user.name  # Some like: Bob Marley
    #:      user = mixer.blend(User, name=mixer.fake)
    #:      print user.name  # Some like: Fdjw4das
    #:
    #: This is also usefull on ORM model generation for randomize fields
    #: with default values (or null).
    random = RANDOM

    #: When you generate some ORM models you can set value for related fields
    #: from database (select by random)
    select = SELECT

    #: Virtual link on the mixed object.
    #: ::
    #:
    #:      mixer = Mixer()
    #:      # here `mixer.mix` points on a generated `User` instance
    #:      user = mixer.blend(User, username=mixer.mix.first_name)
    #:      assert user.username == user.first_name
    #:
    #:      # here `mixer.mix` points on a generated `Message.author` instance
    #:      message = mixer.blend(Message, author__name=mixer.mix.login)
    #:
    #:      # Mixer mix can get a function
    #:      message = mixer.blend(Message, title=mixer.mix.author(
    #:          lambda author: 'Author: %s' % author.name
    #:      ))
    mix = Mix()

    # generator's controller class
    type_mixer_cls = TypeMixer

    def __init__(self, fake=True, generator=None, **params):
        """Initialize Mixer instance.

        :param fake: (True) Generate fake data instead of random data.
        :param generator: (:class:`~mixer.main.Generator`) A class for
                          generation values for types

        """
        self.params = params
        self.generator = generator
        self.fake = fake

    def __repr__(self):
        return "<Mixer [{0}]>".format('fake' if self.fake else 'rand')

    def blend(self, scheme, **values):
        """Generate instance of `scheme`.

        :param scheme: Scheme class for generation or string with class path.
        :param values: Keyword params with predefined values

        ::

            mixer = Mixer()

            mixer.blend(SomeSheme, active=True)
            print scheme.active  # True

            mixer.blend('module.SomeSheme', active=True)
            print scheme.active  # True

        """
        type_mixer = self.type_mixer_cls(
            scheme, mixer=self, fake=self.fake, generator=self.generator)
        return type_mixer.blend(**values)

    @staticmethod
    def post_generate(target):
        return target

    @staticmethod
    def sequence(func=None):
        """ Create sequence for predefined values. It makes a infinity loop
            with given function where does increment the counter on each
            iteration.

            :param func: Function takes one argument or a format string. If
                         func is equal string it should be using as format
                         string.

                         By default function is equal 'lambda x: x'.

            Mixer can uses a generators.
            ::

                gen = (name for name in ['test0', 'test1', 'test2'])
                for counter in range(3):
                    mixer.blend(Scheme, name=gen)

            Mixer.sequence is a helper for create generators from functions.

            ::

                for counter in range(3):
                    mixer.blend(Scheme, name=mixer.sequence(
                        lambda c: 'test%s' % c
                    ))

            Short format is a python formating string

            ::

                for counter in range(3):
                    mixer.blend(Scheme, name=mixer.sequence('test{0}'))


        """
        if isinstance(func, six.string_types):
            func = func.format

        elif func is None:
            func = lambda x: x

        def gen():
            counter = 0
            while True:
                yield func(counter)
                counter += 1
        return gen()

    def cycle(self, count=5):
        """ Generate a few objects. Syntastic sugar for cycles.

            :param count: List of objects or integer.

            ::

                users = mixer.cycle(5).blend('somemodule.User')

                profiles = mixer.cycle(5).blend(
                    'somemodule.Profile', user=mixer.sequence(users))

                apples = mixer.cycle(10).blend(
                    Apple, title=mixer.sequence('apple_{0}')

        """
        return MetaMixer(self, count)


# Default mixer
mixer = Mixer()

# lint_ignore=C901,W0622,F0401,W0621,W0231

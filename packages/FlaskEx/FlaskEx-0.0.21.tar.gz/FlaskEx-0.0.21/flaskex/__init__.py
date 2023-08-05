import re
from os import environ
from logging import StreamHandler, INFO
from functools import wraps
from datetime import datetime

import flask
from flask import (
    g, request, Blueprint as Blueprint_, render_template, flash
)
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import wtf
import flask.ext.sqlalchemy
from flask_debugtoolbar import DebugToolbarExtension
from pyjade.ext.jinja import PyJadeExtension
from facebook import parse_signed_request
from pytz import utc
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy.sql import exists
from wtforms.fields import HiddenField
from werkzeug.routing import BaseConverter

from ex import ex

_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
_underscorer2 = re.compile('([a-z0-9])([A-Z])')


def underscored(s):
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()


class ShortCuts(object):
    def proute(self, *args, **kwargs):
        kwargs['methods'] = ['POST']
        return self.route(*args, **kwargs)

    def pgroute(self, *args, **kwargs):
        kwargs['methods'] = ['GET', 'POST']
        return self.route(*args, **kwargs)


# http://stackoverflow.com/questions/5870188
class RegexConverter(BaseConverter):
    def __init__(self, url_map, regex):
        super(RegexConverter, self).__init__(url_map)
        # BaseConveter will handle other things
        self.regex = regex


class Flask(ShortCuts, flask.Flask):
    def __init__(self, *args, **kwargs):
        super(Flask, self).__init__(*args, **kwargs)
        # regist jade
        self.jinja_env.add_extension(PyJadeExtension)
        self.jinja_env.pyjade.options['pretty'] = 'JADE_PRETTY' in environ
        # redist external template
        self.register_blueprint(ex)
        # connect URL Converters
        self.url_map.converters['re'] = RegexConverter
        # hook config.from_object
        # because some extra settings needs config
        _config_from_object = self.config.from_object

        def config_from_object(*args, **kwargs):
            _config_from_object(*args, **kwargs)
            self.config['SQLALCHEMY_ECHO'] = 'SQLALCHEMY_ECHO' in environ
            self.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = \
                'DEBUG_TB_INTERCEPT_REDIRECTS' in environ
            if self.debug:
                DebugToolbarExtension(self)
            else:
                self.logger.addHandler(StreamHandler())
                self.logger.setLevel(INFO)
        self.config.from_object = config_from_object

    # auto escape jade files too
    def select_jinja_autoescape(self, filename):
        if filename and filename.endswith('.jade'):
            return True
        return super(Flask, self).select_jinja_autoescape(filename)

    def with_context(self, func):
        @wraps(func)
        def _func(*args, **kwargs):
            with self.app_context():
                return func(*args, **kwargs)
        return _func


# extra Features for Facebook
class FlaskFacebook(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskFacebook, self).__init__(*args, **kwargs)

        @self.before_request
        def _before_request():
            signed_request = request.form.get('signed_request', None)
            if signed_request:
                g.signed_request = \
                    parse_signed_request(
                        signed_request, self.config['FACEBOOK_SECRET']
                    )


class Blueprint(ShortCuts, Blueprint_):
    def templated(self, template):
        # if arguments is function, act as calling with None template name
        if hasattr(template, '__call__'):
            return self.templated(None)(template)

        def _templated(f):
            @wraps(f)
            def decorator(*args, **kwargs):
                ctx = f(*args, **kwargs)
                if isinstance(ctx, dict):
                    template_name = template
                    if template_name is None:
                        template_name = self.name + '/' + f.__name__ + '.jade'
                    return render_template(template_name, **ctx)
                return ctx
            return decorator
        return _templated


# http://flask.pocoo.org/docs/patterns/viewdecorators/#templating-decorator
def templated(template_or_view_func):
    # if arguments is function, act as calling with None template name
    if hasattr(template_or_view_func, '__call__'):
        return templated(None)(template_or_view_func)

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template_or_view_func
            if template_name is None:
                template_name = request.endpoint \
                    .replace('.', '/') + '.jade'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator


def success(msg):
    flash(msg, 'success')


def url_for(*args, **kwargs):
    return flask.url_for(*args, **kwargs)

# looks stupid, but it works...
models = {}
_BoundDeclarativeMeta = flask.ext.sqlalchemy._BoundDeclarativeMeta


class BoundDeclarativeMeta(_BoundDeclarativeMeta):
    def __init__(cls, name, bases, d):
        super(BoundDeclarativeMeta, cls).__init__(name, bases, d)
        if name != 'Model':
            models[underscored(name)] = cls
# patch  _BoundDeclarativeMeta
flask.ext.sqlalchemy._BoundDeclarativeMeta = BoundDeclarativeMeta


class SQLAlchemy(SQLAlchemy):
    def __init__(self, app, *args, **kwargs):
        super(SQLAlchemy, self).__init__(app, *args, **kwargs)

        @app.url_value_preprocessor
        def model_preprocessor(endpoint, values):
            if values:
                for key, id in values.items():
                    model_name = key[:-3]
                    model = models.get(model_name, None)
                    if model:
                        if id:
                            if hasattr(id, '__call__'):
                                value = id()
                            else:
                                value = model.query.get_or_404(id)
                        else:
                            value = model()
                        del values[key]
                        values[model_name] = value


def utc_now():
    return datetime.utcnow().replace(tzinfo=utc)


def timestamp(dt):
    return int(dt.strftime("%s"))


class ShortHandMixin(object):
    @classmethod
    def exists(cls, clause):
        if not isinstance(clause, ClauseElement):
            clause = cls.id == clause
        return bool(
            cls.query.session.query(exists((cls.id,)).where(clause)).scalar()
        )


class PKMixin(object):
    id = Column(Integer, primary_key=True)

    @property
    def is_new(self):
        return self.id is None


class TimesMixin(object):
    created_at = Column(DateTime(True), default=utc_now)
    updated_at = Column(
        DateTime(True), default=utc_now, onupdate=utc_now
    )


class AllMixin(PKMixin, TimesMixin, ShortHandMixin):
    pass


class Form(wtf.Form):
    @property
    def hidden_fields(self):
        return tuple(field for field in self if isinstance(field, HiddenField))

    @property
    def fields(self):
        return tuple(
            field for field in self if not isinstance(field, HiddenField)
        )

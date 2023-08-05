
#
# spyne - Copyright (C) Spyne contributors.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#

"""
An opinionated web framework built on top of Spyne, SQLAlchemy and Twisted.
"""

from __future__ import absolute_import

from spyne.application import Application as AppBase
from spyne.error import Fault
from spyne.error import InternalError
from spyne.error import ResourceNotFoundError
from spyne.service import ServiceBase
from spyne.util.email import email_exception

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from twisted.python import log
from twisted.python.threadpool import ThreadPool
from twisted.internet import reactor
from twisted.internet.threads import deferToThreadPool


EXCEPTION_ADDRESS = "admin@gezi.io"


try:
    import colorama
    colorama.init()

    from colorama.ansi import Fore
    RED = Fore.RED
    GREEN = Fore.GREEN
    RESET = Fore.RESET

except ImportError:
    RED = ""
    GREEN = ""
    RESET = ""


class ReaderServiceBase(ServiceBase):
    pass


class WriterServiceBase(ServiceBase):
    pass


def _on_method_call(ctx):
    ctx.udc = Context(ctx.app.db, ctx.app.Session)

def _on_method_context_closed(ctx):
    error = None
    if ctx.in_error is not None:
        error = ctx.in_error

    elif ctx.out_error is not None:
        error = ctx.out_error

    if error is None:
        log.msg('%s[OK]%s %r => %r' % (GREEN, RESET, ctx.in_object, ctx.out_object))
    elif isinstance(error, Fault):
        log.msg('%s[CE]%s %r => %r' % (RED, RESET, ctx.in_object, error))
    else:
        log.msg('%s[UE]%s %r => %r' % (RED, RESET, ctx.in_object, error))

    if ctx.udc is not None:
        ctx.udc.close()

class Application(AppBase):
    def __init__(self, services, tns, name=None, in_protocol=None,
                 out_protocol=None, db=None):
        AppBase.__init__(self, services, tns, name, in_protocol, out_protocol)

        self.event_manager.add_listener("method_call", _on_method_call)
        self.event_manager.add_listener("method_context_closed",
                                                      _on_method_context_closed)

        self.db = db
        self.Session = sessionmaker(bind=db)

    def call_wrapper(self, ctx):
        try:
            return ctx.service_class.call_wrapper(ctx)

        except NoResultFound:
            raise ResourceNotFoundError(ctx.in_object)

        except Fault, e:
            log.err()
            raise

        except Exception, e:
            log.err()
            # This should not happen! Let the team know via email!
            email_exception(EXCEPTION_ADDRESS)
            raise InternalError(e)


def _user_callables(d):
    for k,v in d.items():
        if callable(v) and not k in ('__init__', '__metaclass__'):
            yield k,v

def _et(f):
    def _wrap(*args, **kwargs):
        self = args[0]

        try:
            return f(*args, **kwargs)

        except NoResultFound:
            raise ResourceNotFoundError(self.ctx.in_object)

        except Fault, e:
            log.err()
            raise

        except Exception, e:
            log.err()
            # This should not happen! Let the team know via email!
            email_exception(EXCEPTION_ADDRESS)
            raise InternalError(e)
    return _wrap

class DBThreadPool(ThreadPool):
    def __init__(self, engine, verbose=False):
        if engine.dialect.name == 'sqlite':
            pool_size = 1

            ThreadPool.__init__(self, minthreads=1, maxthreads=1)
        else:
            ThreadPool.__init__(self)

        self.engine = engine
        reactor.callWhenRunning(self.start)

    def start(self):
        reactor.addSystemEventTrigger('during', 'shutdown', self.stop)
        ThreadPool.start(self)


class DalMeta(type(object)):
    def __new__(cls, cls_name, cls_bases, cls_dict):
        for k, v in _user_callables(cls_dict):
            def _w2(_user_callable):
                def _wrap(*args, **kwargs):
                    return deferToThreadPool(reactor, retval._pool, 
                                            _et(_user_callable), *args, **kwargs)
                return _wrap
            cls_dict[k] = _w2(v)

        retval = type(object).__new__(cls, cls_name, cls_bases, cls_dict)
        return retval

    @property
    def bind(self):
        return self._db

    @bind.setter
    def bind(self, what):
        self._db = what
        self._pool = DBThreadPool(what)


class DalBase(object):
    __metaclass__ = DalMeta

    _db = None
    _pool = None

    def __init__(self, ctx):
        self.ctx = ctx
        self.session = ctx.udc.session
        if ctx.udc.session is None:
            self.session = ctx.udc.session = ctx.udc.Session()


class Context(object):
    def __init__(self, db, Session=None):
        self.db = db
        self.Session = Session
        self.rd = None
        self.ru = None
        self.session = None

    def close(self):
        if self.session is not None:
            self.session.close()

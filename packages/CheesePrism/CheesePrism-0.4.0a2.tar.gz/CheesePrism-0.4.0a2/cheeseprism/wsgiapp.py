from .jenv import EnvFactory
from cheeseprism.auth import BasicAuthenticationPolicy
from cheeseprism.resources import App
from functools import partial
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.settings import asbool
from pyramid_jinja2 import renderer_factory
import futures
import logging
import multiprocessing
import signal
import sys
import os

logger = logging.getLogger(__name__)


def main(global_config, **settings):
    settings = dict(global_config, **settings)

    settings.setdefault('jinja2.i18n.domain', 'CheesePrism')

    session_factory = UnencryptedCookieSessionFactoryConfig('cheeseprism')
    config = Configurator(root_factory=App, settings=settings,
                          session_factory=session_factory,
                          authentication_policy=\
                          BasicAuthenticationPolicy(BasicAuthenticationPolicy.noop_check))

    setup_workers(config.registry)

    config.add_translation_dirs('locale/')
    config.include('pyramid_jinja2')
    config.add_renderer('.html', renderer_factory)
    config.add_static_view('static', 'static')
    config.include('.request')
    config.scan('.views')
    config.include('.index')
    config.add_route('package', 'package/{name}/{version}')
    config.add_view('.views.from_pypi', route_name='package')

    tempspec = settings.get('cheeseprism.index_templates', '')
    config.registry['cp.index_templates'] = EnvFactory.from_str(tempspec)

    if asbool(settings.get('cheeseprism.pipcache_mirror', False)):
        config.include('.sync.pip')

    if asbool(settings.get('cheeseprism.auto_sync', False)):
        config.include('.sync.auto')

    return config.make_wsgi_app()


def sig_handler(executor, sig, frame, wait=True):
    logger.warn("Signal %d recieved: wait: %s", sig, wait)
    executor.shutdown(wait)
    logger.info("Executor shutdown complete")


def ping_proc(i):
    pid = os.getpid()
    logger.debug("worker %s up: %s", i, pid)
    return pid


def setup_workers(registry, handler=sig_handler):
    """
    ATT: Sensitive voodoo. Workers must be setup before any other
    threads are launched. Workers must be initialized before signals
    are registered.
    """
    settings = registry.settings
    executor_type = settings.get('cheeseprism.futures', 'thread')
    executor = executor_type != 'process' and futures.ThreadPoolExecutor \
      or futures.ProcessPoolExecutor

    workers = int(settings.get('cheeseprism.futures.workers', 0))
    if executor_type == 'process' and workers <= 0:
        workers = multiprocessing.cpu_count() + 1
    else:
        workers = workers <= 0 and 10 or workers

    logging.info("PID %s using %s executor with %s workers", os.getpid(), executor_type, workers)
    executor = registry['cp.executor'] = executor(workers)

    # -- This initializes our processes/threads
    workers = [str(pid) for pid in executor.map(ping_proc, range(workers))]
    logger.info("workers: %s", " ".join(workers))

    # -- Register signals after init so to not have an echo effect
    for sig in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT, signal.SIGQUIT):
        signal.signal(sig, partial(sig_handler, executor))

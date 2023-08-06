#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Pika

A set of custom classes to better integration of pika with PySide
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from itertools import ifilter

__all__ = ['PySideReconnectionStrategy', 'PySideConnection']

# Pyside requirements
from PySide.QtCore import QObject, QSocketNotifier, QCoreApplication, QTimer
from PySide.QtNetwork import QNetworkConfigurationManager, QNetworkSession

# Project requirements
from sleipnir.core.decorators import cached

#Pika requirements
from pika.reconnection_strategies import ReconnectionStrategy
from pika.adapters.base_connection import BaseConnection, READ, WRITE


class PySideReconnectionStrategy(ReconnectionStrategy):

    can_reconnect = True

    def __init__(self):
        self.manager = QNetworkConfigurationManager()
        self.session = self._session()
        self.manager.onlineStateChanged.connect(self._connect)

    def _session(self):
        return QNetworkSession(self.manager.defaultConfiguration())

    def _connect(self, is_connected):
        if is_connected is False:
            # create a new session
            self.session = self._session()
            # start session if required
            caps = self.manager.capabilities()
            if caps & QNetworkConfigurationManager.CanStartAndStopInterfaces:
                self.session.open()
                self.session.waitForOpened(-1)

    def on_connect_attempt(self, conn):
        self._connect(self.manager.isOnline())

    def on_connection_open(self, conn):
        caps = self.manager.capabilities()
        if caps & QNetworkConfigurationManager.ForcedRoaming:
            reconnect = conn.force_reconnect
            self.session.newConfigurationActivated.connect(reconnect)

    def on_connection_closed(self, conn):
        conn._reconnect() if not self.is_active else None


class PySideTimer(object):
    def __init__(self, container, callback, single_shot):
        self.callback = callback
        self.single_shot = single_shot
        self.first_run = False

    def register(self, pool, deadline):
        timeout_id = pool.startTimer(deadline)
        pool.timers[timeout_id] = self
        return timeout_id

    def unregister(self, pool, timeout_id):
        pool.killTimer(timeout_id)
        del pool[timeout_id]

    def __call__(self, pool, timeout_id):
        self.callback()
        if self.single_shot:
            self.unregister(pool, timeout_id)


class PySideConnectionPoller(QObject):

    def __init__(self, connection):
        # Set container
        self.parent = connection

    def __iter__(self):
        return iter((self.reader, self.writer,))

    def _connect(self, notifier_type, callback):
        notifier = QSocketNotifier(self.parent.fileno, notifier_type)
        notifier.activated.connect(callback)
        notifier.setEnabled(False)
        return notifier

    def _read(self, _):
        self.parent._handle_read()
        self.parent._manage_event_state()

    def _write(self, _):
        self.parent._handle_write()
        self.parent._manage_event_state()

    def _error(self, _):
        self.parent._handle_disconnect()

    def poll(self):
        # Create Notifiers
        self.reader = self._connect(QSocketNotifier.Read,  self._read)
        self.writer = self._connect(QSocketNotifier.Write, self._write)
        # Create Error watcher
        self.errors = self._connect(QSocketNotifier.Exception, self._error)
        self.errors.setEnabled(True)
        # update handlers
        self.parent.ioloop.update_handler(None, self.parent.event_state)

    def unpoll(self):
        self.reader = self.writer = self.errors = None


class PySideConnection(BaseConnection):

    def __iter__(self):
        return iter(self.notifiers)

    def _adapter_connect(self):
        # Connect (blockignly!) to the server
        BaseConnection._adapter_connect(self)
        self.event_state |= WRITE
        # Setup the IOLoop
        self.ioloop = IOLoop(self.notifiers)
        # Let everyone know we're connected
        self._on_connected()

    def _flush_outbound(self):
        self._manage_event_state()

    @property
    def fileno(self):
        return self.socket.fileno()

    @property
    @cached
    def notifiers(self):
        return PySideConnectionPoller(self)


class IOLoop(QObject):
    def __init__(self, poller):
        self.poller = poller
        self.timers = {}

    def timerEvent(self, event):
        self.timers[event.timerId()](self, timeout_id)

    def add_timeout(self, deadline, callback, oneshot=False):
        deadline = deadline - time.time()
        return PySideTimer(self, callback, oneshot).register(self, deadline)

    def add_soft_timeout(self, min_time, max_time, callback, oneshot=False):
        raise NotImplementedError

    def remove_timeout(self, handler):
        self.timers[timeout_id].unregister(self, handler)

    def stop(self):
        [timer.unregister(self, key) for key, timer in self.timers]
        QTimer.singleShot(0, self.poller.unpoll)
        self.exec_ and QCoreApplication.instance().quit()

    def start(self, exec_=True):
        self.exec_ = exec_
        QTimer.singleShot(0, self.poller.poll)
        self.exec_ and QCoreApplication.instance().exec_()

    def remove_handler(self, fdn=None):
        [notifier.setEnabled(False) for notifier in self.poller]

    def update_handler(self, fdn, event_state):
        self.remove_handler()
        # update notifiers state
        if event_state & READ:
            self.poller.reader.setEnabled(True)
        if event_state & WRITE:
            self.poller.writer.setEnabled(True)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests if the daemon forces a simualte during run."""

import logging
import time
import unittest

from gi.repository import GObject
import dbus

import aptdaemon.client
import aptdaemon.loop
import aptdaemon.enums

import aptdaemon.test

DEBUG = True


class DaemonTest(aptdaemon.test.AptDaemonTestCase):

    """Test the python client."""

    def setUp(self):
        """Setup a chroot, run the aptdaemon and a fake PolicyKit daemon."""
        # Setup chroot
        self.chroot = aptdaemon.test.Chroot()
        self.chroot.setup()
        self.addCleanup(self.chroot.remove)
        # Start aptdaemon with the chroot on the session bus
        self.start_dbus_daemon()
        self.bus = dbus.bus.BusConnection(self.dbus_address)
        self.start_session_aptd(self.chroot.path)
        # Start the fake PolikcyKit daemon
        self.start_fake_polkitd()
        time.sleep(1)

    def _on_finished(self, trans, exit):
        """Callback to stop the mainloop after a transaction is done."""
        aptdaemon.loop.mainloop.quit()

    def test_detect_unauthenticated(self):
        """Test if the installation of an unauthenticated packages fails
        if simulate hasn't been called explicitly before.
        """
        self.chroot.add_test_repository(copy_sig=False)
        self.client = aptdaemon.client.AptClient(self.bus)
        trans = self.client.install_packages(["silly-base"])
        trans.connect("finished", self._on_finished)
        trans.run()
        aptdaemon.loop.mainloop.run()
        self.assertEqual(trans.exit, aptdaemon.enums.EXIT_FAILED)
        self.assertEqual(trans.error.code,
                         aptdaemon.enums.ERROR_PACKAGE_UNAUTHENTICATED)
        self.assertEqual(trans.unauthenticated, ["silly-base"])

    def test_environment(self):
        """Ensure that the test environment works."""
        self.chroot.add_test_repository()
        self.client = aptdaemon.client.AptClient(self.bus)
        trans = self.client.install_packages(["silly-base"])
        trans.connect("finished", self._on_finished)
        trans.run()
        aptdaemon.loop.mainloop.run()
        self.assertEqual(trans.exit, aptdaemon.enums.EXIT_SUCCESS)


if __name__ == "__main__":
    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()

# vim: ts=4 et sts=4

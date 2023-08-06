# -*- coding: utf-8 -*-
# statuspanel.py
# Copyright (C) 2013 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Status Panel widget implementation
"""
import logging

from datetime import datetime
from functools import partial

from PySide import QtCore, QtGui

from leap.bitmask.services.eip.vpnprocess import VPNManager
from leap.bitmask.platform_init import IS_WIN, IS_LINUX
from leap.bitmask.util import first
from leap.common.check import leap_assert, leap_assert_type
from leap.common.events import register
from leap.common.events import events_pb2 as proto

from ui_statuspanel import Ui_StatusPanel

logger = logging.getLogger(__name__)


class RateMovingAverage(object):
    """
    Moving window average for calculating
    upload and download rates.
    """
    SAMPLE_SIZE = 5

    def __init__(self):
        """
        Initializes an empty array of fixed size
        """
        self.reset()

    def reset(self):
        self._data = [None for i in xrange(self.SAMPLE_SIZE)]

    def append(self, x):
        """
        Appends a new data point to the collection.

        :param x: A tuple containing timestamp and traffic points
                  in the form (timestamp, traffic)
        :type x: tuple
        """
        self._data.pop(0)
        self._data.append(x)

    def get(self):
        """
        Gets the collection.
        """
        return self._data

    def get_average(self):
        """
        Gets the moving average.
        """
        data = filter(None, self.get())
        traff = [traffic for (ts, traffic) in data]
        times = [ts for (ts, traffic) in data]

        try:
            deltatraffic = traff[-1] - first(traff)
            deltat = (times[-1] - first(times)).seconds
        except IndexError:
            deltatraffic = 0
            deltat = 0

        try:
            rate = float(deltatraffic) / float(deltat) / 1024
        except ZeroDivisionError:
            rate = 0

        # In some cases we get negative rates
        if rate < 0:
            rate = 0

        return rate

    def get_total(self):
        """
        Gets the total accumulated throughput.
        """
        try:
            return self._data[-1][1] / 1024
        except TypeError:
            return 0


class StatusPanelWidget(QtGui.QWidget):
    """
    Status widget that displays the current state of the LEAP services
    """

    start_eip = QtCore.Signal()
    stop_eip = QtCore.Signal()

    DISPLAY_TRAFFIC_RATES = True
    RATE_STR = "%14.2f KB/s"
    TOTAL_STR = "%14.2f Kb"

    MAIL_OFF_ICON = ":/images/mail-unlocked.png"
    MAIL_ON_ICON = ":/images/mail-locked.png"

    _soledad_event = QtCore.Signal(object)
    _smtp_event = QtCore.Signal(object)
    _imap_event = QtCore.Signal(object)
    _keymanager_event = QtCore.Signal(object)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self._systray = None
        self._action_eip_status = None

        self.ui = Ui_StatusPanel()
        self.ui.setupUi(self)

        self.ui.btnEipStartStop.setEnabled(False)
        self.ui.btnEipStartStop.clicked.connect(
            self.start_eip)

        self.hide_status_box()

        # Set the EIP status icons
        self.CONNECTING_ICON = None
        self.CONNECTED_ICON = None
        self.ERROR_ICON = None
        self.CONNECTING_ICON_TRAY = None
        self.CONNECTED_ICON_TRAY = None
        self.ERROR_ICON_TRAY = None
        self._set_eip_icons()

        self._set_traffic_rates()
        self._make_status_clickable()

        register(signal=proto.KEYMANAGER_LOOKING_FOR_KEY,
                 callback=self._mail_handle_keymanager_events,
                 reqcbk=lambda req, resp: None)

        register(signal=proto.KEYMANAGER_KEY_FOUND,
                 callback=self._mail_handle_keymanager_events,
                 reqcbk=lambda req, resp: None)

        # register(signal=proto.KEYMANAGER_KEY_NOT_FOUND,
        #          callback=self._mail_handle_keymanager_events,
        #          reqcbk=lambda req, resp: None)

        register(signal=proto.KEYMANAGER_STARTED_KEY_GENERATION,
                 callback=self._mail_handle_keymanager_events,
                 reqcbk=lambda req, resp: None)

        register(signal=proto.KEYMANAGER_FINISHED_KEY_GENERATION,
                 callback=self._mail_handle_keymanager_events,
                 reqcbk=lambda req, resp: None)

        register(signal=proto.KEYMANAGER_DONE_UPLOADING_KEYS,
                 callback=self._mail_handle_keymanager_events,
                 reqcbk=lambda req, resp: None)

        register(signal=proto.SOLEDAD_DONE_DOWNLOADING_KEYS,
                 callback=self._mail_handle_soledad_events,
                 reqcbk=lambda req, resp: None)

        register(signal=proto.SOLEDAD_DONE_UPLOADING_KEYS,
                 callback=self._mail_handle_soledad_events,
                 reqcbk=lambda req, resp: None)

        register(signal=proto.SMTP_SERVICE_STARTED,
                 callback=self._mail_handle_smtp_events,
                 reqcbk=lambda req, resp: None)

        register(signal=proto.SMTP_SERVICE_FAILED_TO_START,
                 callback=self._mail_handle_smtp_events,
                 reqcbk=lambda req, resp: None)

        register(signal=proto.IMAP_SERVICE_STARTED,
                 callback=self._mail_handle_imap_events,
                 reqcbk=lambda req, resp: None)

        register(signal=proto.IMAP_SERVICE_FAILED_TO_START,
                 callback=self._mail_handle_imap_events,
                 reqcbk=lambda req, resp: None)

        register(signal=proto.IMAP_UNREAD_MAIL,
                 callback=self._mail_handle_imap_events,
                 reqcbk=lambda req, resp: None)

        self._set_long_mail_status("")
        self.ui.lblUnread.setVisible(False)

        self._smtp_started = False
        self._imap_started = False

        self._soledad_event.connect(
            self._mail_handle_soledad_events_slot)
        self._imap_event.connect(
            self._mail_handle_imap_events_slot)
        self._smtp_event.connect(
            self._mail_handle_smtp_events_slot)
        self._keymanager_event.connect(
            self._mail_handle_keymanager_events_slot)

    def _make_status_clickable(self):
        """
        Makes upload and download figures clickable.
        """
        onclicked = self._on_VPN_status_clicked
        self.ui.btnUpload.clicked.connect(onclicked)
        self.ui.btnDownload.clicked.connect(onclicked)

    def _on_VPN_status_clicked(self):
        """
        SLOT
        TRIGGER: self.ui.btnUpload.clicked
                 self.ui.btnDownload.clicked

        Toggles between rate and total throughput display for vpn
        status figures.
        """
        self.DISPLAY_TRAFFIC_RATES = not self.DISPLAY_TRAFFIC_RATES
        self.update_vpn_status(None)  # refresh

    def _set_traffic_rates(self):
        """
        Initializes up and download rates.
        """
        self._up_rate = RateMovingAverage()
        self._down_rate = RateMovingAverage()

        self.ui.btnUpload.setText(self.RATE_STR % (0,))
        self.ui.btnDownload.setText(self.RATE_STR % (0,))

    def _reset_traffic_rates(self):
        """
        Resets up and download rates, and cleans up the labels.
        """
        self._up_rate.reset()
        self._down_rate.reset()
        self.update_vpn_status(None)

    def _update_traffic_rates(self, up, down):
        """
        Updates up and download rates.

        :param up: upload total.
        :type up: int
        :param down: download total.
        :type down: int
        """
        ts = datetime.now()
        self._up_rate.append((ts, up))
        self._down_rate.append((ts, down))

    def _get_traffic_rates(self):
        """
        Gets the traffic rates (in KB/s).

        :returns: a tuple with the (up, down) rates
        :rtype: tuple
        """
        up = self._up_rate
        down = self._down_rate

        return (up.get_average(), down.get_average())

    def _get_traffic_totals(self):
        """
        Gets the traffic total throughput (in Kb).

        :returns: a tuple with the (up, down) totals
        :rtype: tuple
        """
        up = self._up_rate
        down = self._down_rate

        return (up.get_total(), down.get_total())

    def _set_eip_icons(self):
        """
        Sets the EIP status icons for the main window and for the tray

        MAC   : dark icons
        LINUX : dark icons in window, light icons in tray
        WIN   : light icons
        """
        EIP_ICONS = EIP_ICONS_TRAY = (
            ":/images/conn_connecting-light.png",
            ":/images/conn_connected-light.png",
            ":/images/conn_error-light.png")

        if IS_LINUX:
            EIP_ICONS_TRAY = (
                ":/images/conn_connecting.png",
                ":/images/conn_connected.png",
                ":/images/conn_error.png")
        elif IS_WIN:
            EIP_ICONS = EIP_ICONS_TRAY = (
                ":/images/conn_connecting.png",
                ":/images/conn_connected.png",
                ":/images/conn_error.png")

        self.CONNECTING_ICON = QtGui.QPixmap(EIP_ICONS[0])
        self.CONNECTED_ICON = QtGui.QPixmap(EIP_ICONS[1])
        self.ERROR_ICON = QtGui.QPixmap(EIP_ICONS[2])

        self.CONNECTING_ICON_TRAY = QtGui.QPixmap(EIP_ICONS_TRAY[0])
        self.CONNECTED_ICON_TRAY = QtGui.QPixmap(EIP_ICONS_TRAY[1])
        self.ERROR_ICON_TRAY = QtGui.QPixmap(EIP_ICONS_TRAY[2])

    def set_systray(self, systray):
        """
        Sets the systray object to use.

        :param systray: Systray object
        :type systray: QtGui.QSystemTrayIcon
        """
        leap_assert_type(systray, QtGui.QSystemTrayIcon)
        self._systray = systray

    def set_action_eip_startstop(self, action_eip_startstop):
        """
        Sets the action_eip_startstop to use.

        :param action_eip_startstop: action_eip_status to be used
        :type action_eip_startstop: QtGui.QAction
        """
        self._action_eip_startstop = action_eip_startstop

    def set_action_eip_status(self, action_eip_status):
        """
        Sets the action_eip_status to use.

        :param action_eip_status: action_eip_status to be used
        :type action_eip_status: QtGui.QAction
        """
        leap_assert_type(action_eip_status, QtGui.QAction)
        self._action_eip_status = action_eip_status

    def set_action_mail_status(self, action_mail_status):
        """
        Sets the action_mail_status to use.

        :param action_mail_status: action_mail_status to be used
        :type action_mail_status: QtGui.QAction
        """
        leap_assert_type(action_mail_status, QtGui.QAction)
        self._action_mail_status = action_mail_status

    def set_global_status(self, status, error=False):
        """
        Sets the global status label.

        :param status: status message
        :type status: str or unicode
        :param error: if the status is an erroneous one, then set this
                      to True
        :type error: bool
        """
        leap_assert_type(error, bool)
        if error:
            status = "<font color='red'><b>%s</b></font>" % (status,)
        self.ui.lblGlobalStatus.setText(status)
        self.ui.globalStatusBox.show()

    def hide_status_box(self):
        """
        Hide global status box.
        """
        self.ui.globalStatusBox.hide()

    def set_eip_status(self, status, error=False):
        """
        Sets the status label at the VPN stage to status

        :param status: status message
        :type status: str or unicode
        :param error: if the status is an erroneous one, then set this
                      to True
        :type error: bool
        """
        leap_assert_type(error, bool)

        self._systray.setToolTip(status)
        if error:
            status = "<font color='red'>%s</font>" % (status,)
        self.ui.lblEIPStatus.setText(status)

    def set_startstop_enabled(self, value):
        """
        Enable or disable btnEipStartStop and _action_eip_startstop
        based on value

        :param value: True for enabled, False otherwise
        :type value: bool
        """
        leap_assert_type(value, bool)
        self.ui.btnEipStartStop.setEnabled(value)
        self._action_eip_startstop.setEnabled(value)

    def eip_pre_up(self):
        """
        Triggered when the app activates eip.
        Hides the status box and disables the start/stop button.
        """
        self.hide_status_box()
        self.set_startstop_enabled(False)

    def eip_started(self):
        """
        Sets the state of the widget to how it should look after EIP
        has started
        """
        self.ui.btnEipStartStop.setText(self.tr("Turn OFF"))
        self.ui.btnEipStartStop.disconnect(self)
        self.ui.btnEipStartStop.clicked.connect(
            self.stop_eip)

    def eip_stopped(self):
        """
        Sets the state of the widget to how it should look after EIP
        has stopped
        """
        self._reset_traffic_rates()
        self.ui.btnEipStartStop.setText(self.tr("Turn ON"))
        self.ui.btnEipStartStop.disconnect(self)
        self.ui.btnEipStartStop.clicked.connect(
            self.start_eip)

    def set_icon(self, icon):
        """
        Sets the icon to display for EIP

        :param icon: icon to display
        :type icon: QPixmap
        """
        self.ui.lblVPNStatusIcon.setPixmap(icon)

    def update_vpn_status(self, data):
        """
        SLOT
        TRIGGER: VPN.status_changed

        Updates the download/upload labels based on the data provided
        by the VPN thread.

        :param data: a dictionary with the tcp/udp write and read totals.
                     If data is None, we just will refresh the display based
                     on the previous data.
        :type data: dict
        """
        if data:
            upload = float(data[VPNManager.TCPUDP_WRITE_KEY] or "0")
            download = float(data[VPNManager.TCPUDP_READ_KEY] or "0")
            self._update_traffic_rates(upload, download)

        if self.DISPLAY_TRAFFIC_RATES:
            uprate, downrate = self._get_traffic_rates()
            upload_str = self.RATE_STR % (uprate,)
            download_str = self.RATE_STR % (downrate,)

        else:  # display total throughput
            uptotal, downtotal = self._get_traffic_totals()
            upload_str = self.TOTAL_STR % (uptotal,)
            download_str = self.TOTAL_STR % (downtotal,)

        self.ui.btnUpload.setText(upload_str)
        self.ui.btnDownload.setText(download_str)

    def update_vpn_state(self, data):
        """
        SLOT
        TRIGGER: VPN.state_changed

        Updates the displayed VPN state based on the data provided by
        the VPN thread
        """
        status = data[VPNManager.STATUS_STEP_KEY]
        self.set_eip_status_icon(status)
        if status == "CONNECTED":
            self.set_eip_status(self.tr("ON"))
            # Only now we can properly enable the button.
            self.set_startstop_enabled(True)
        elif status == "AUTH":
            self.set_eip_status(self.tr("Authenticating..."))
        elif status == "GET_CONFIG":
            self.set_eip_status(self.tr("Retrieving configuration..."))
        elif status == "WAIT":
            self.set_eip_status(self.tr("Waiting to start..."))
        elif status == "ASSIGN_IP":
            self.set_eip_status(self.tr("Assigning IP"))
        elif status == "RECONNECTING":
            self.set_eip_status(self.tr("Reconnecting..."))
        elif status == "ALREADYRUNNING":
            # Put the following calls in Qt's event queue, otherwise
            # the UI won't update properly
            QtCore.QTimer.singleShot(0, self.stop_eip)
            QtCore.QTimer.singleShot(0, partial(self.set_global_status,
                                                self.tr("Unable to start VPN, "
                                                        "it's already "
                                                        "running.")))
        else:
            self.set_eip_status(status)

    def set_eip_status_icon(self, status):
        """
        Given a status step from the VPN thread, set the icon properly

        :param status: status step
        :type status: str
        """
        selected_pixmap = self.ERROR_ICON
        selected_pixmap_tray = self.ERROR_ICON_TRAY
        tray_message = self.tr("Encryption is OFF")
        if status in ("WAIT", "AUTH", "GET_CONFIG",
                      "RECONNECTING", "ASSIGN_IP"):
            selected_pixmap = self.CONNECTING_ICON
            selected_pixmap_tray = self.CONNECTING_ICON_TRAY
            tray_message = self.tr("Turning ON")
        elif status in ("CONNECTED"):
            tray_message = self.tr("Encryption is ON")
            selected_pixmap = self.CONNECTED_ICON
            selected_pixmap_tray = self.CONNECTED_ICON_TRAY

        self.set_icon(selected_pixmap)
        self._systray.setIcon(QtGui.QIcon(selected_pixmap_tray))
        self._action_eip_status.setText(tray_message)

    def set_provider(self, provider):
        self.ui.lblProvider.setText(provider)

    def _set_mail_status(self, status, ready=False):
        """
        Sets the Encrypted Mail status in the label and in the tray icon.

        :param status: the status text to display
        :type status: unicode
        :param ready: if mx is ready or not.
        :type ready: bool
        """
        self.ui.lblMailStatus.setText(status)

        tray_status = self.tr('Encrypted Mail is OFF')

        icon = QtGui.QPixmap(self.MAIL_OFF_ICON)
        if ready:
            icon = QtGui.QPixmap(self.MAIL_ON_ICON)
            tray_status = self.tr('Encrypted Mail is ON')

        self.ui.lblMailIcon.setPixmap(icon)
        self._action_mail_status.setText(tray_status)

    def _mail_handle_soledad_events(self, req):
        """
        Callback for ...

        :param req: Request type
        :type req: leap.common.events.events_pb2.SignalRequest
        """
        self._soledad_event.emit(req)

    def _mail_handle_soledad_events_slot(self, req):
        """
        SLOT
        TRIGGER: _mail_handle_soledad_events

        Reacts to an Soledad event

        :param req: Request type
        :type req: leap.common.events.events_pb2.SignalRequest
        """
        self._set_mail_status(self.tr("Starting..."))

        ext_status = ""

        if req.event == proto.SOLEDAD_DONE_UPLOADING_KEYS:
            ext_status = self.tr("Soledad has started...")
        elif req.event == proto.SOLEDAD_DONE_DOWNLOADING_KEYS:
            ext_status = self.tr("Soledad is starting, please wait...")
        else:
            leap_assert(False,
                        "Don't know how to handle this state: %s"
                        % (req.event))

        self._set_long_mail_status(ext_status)

    def _mail_handle_keymanager_events(self, req):
        """
        Callback for the KeyManager events

        :param req: Request type
        :type req: leap.common.events.events_pb2.SignalRequest
        """
        self._keymanager_event.emit(req)

    def _mail_handle_keymanager_events_slot(self, req):
        """
        SLOT
        TRIGGER: _mail_handle_keymanager_events

        Reacts to an KeyManager event

        :param req: Request type
        :type req: leap.common.events.events_pb2.SignalRequest
        """
        # We want to ignore this kind of events once everything has
        # started
        if self._smtp_started and self._imap_started:
            return

        self._set_mail_status(self.tr("Starting..."))

        ext_status = ""

        if req.event == proto.KEYMANAGER_LOOKING_FOR_KEY:
            ext_status = self.tr("Looking for key for this user")
        elif req.event == proto.KEYMANAGER_KEY_FOUND:
            ext_status = self.tr("Found key! Starting mail...")
        # elif req.event == proto.KEYMANAGER_KEY_NOT_FOUND:
        #     ext_status = self.tr("Key not found!")
        elif req.event == proto.KEYMANAGER_STARTED_KEY_GENERATION:
            ext_status = self.tr("Generating new key, please wait...")
        elif req.event == proto.KEYMANAGER_FINISHED_KEY_GENERATION:
            ext_status = self.tr("Finished generating key!")
        elif req.event == proto.KEYMANAGER_DONE_UPLOADING_KEYS:
            ext_status = self.tr("Starting mail...")
        else:
            leap_assert(False,
                        "Don't know how to handle this state: %s"
                        % (req.event))

        self._set_long_mail_status(ext_status)

    def _mail_handle_smtp_events(self, req):
        """
        Callback for the SMTP events

        :param req: Request type
        :type req: leap.common.events.events_pb2.SignalRequest
        """
        self._smtp_event.emit(req)

    def _mail_handle_smtp_events_slot(self, req):
        """
        SLOT
        TRIGGER: _mail_handle_smtp_events

        Reacts to an SMTP event

        :param req: Request type
        :type req: leap.common.events.events_pb2.SignalRequest
        """
        ext_status = ""

        if req.event == proto.SMTP_SERVICE_STARTED:
            ext_status = self.tr("SMTP has started...")
            self._smtp_started = True
            if self._smtp_started and self._imap_started:
                self._set_mail_status(self.tr("ON"), ready=True)
                ext_status = ""
        elif req.event == proto.SMTP_SERVICE_FAILED_TO_START:
            ext_status = self.tr("SMTP failed to start, check the logs.")
            self._set_mail_status(self.tr("Failed"))
        else:
            leap_assert(False,
                        "Don't know how to handle this state: %s"
                        % (req.event))

        self._set_long_mail_status(ext_status)

    def _mail_handle_imap_events(self, req):
        """
        Callback for the IMAP events

        :param req: Request type
        :type req: leap.common.events.events_pb2.SignalRequest
        """
        self._imap_event.emit(req)

    def _mail_handle_imap_events_slot(self, req):
        """
        SLOT
        TRIGGER: _mail_handle_imap_events

        Reacts to an IMAP event

        :param req: Request type
        :type req: leap.common.events.events_pb2.SignalRequest
        """
        ext_status = None

        if req.event == proto.IMAP_SERVICE_STARTED:
            ext_status = self.tr("IMAP has started...")
            self._imap_started = True
            if self._smtp_started and self._imap_started:
                self._set_mail_status(self.tr("ON"), ready=True)
                ext_status = ""
        elif req.event == proto.IMAP_SERVICE_FAILED_TO_START:
            ext_status = self.tr("IMAP failed to start, check the logs.")
            self._set_mail_status(self.tr("Failed"))
        elif req.event == proto.IMAP_UNREAD_MAIL:
            if self._smtp_started and self._imap_started:
                self.ui.lblUnread.setText(
                    self.tr("%s Unread Emails") % (req.content))
                self.ui.lblUnread.setVisible(req.content != "0")
                self._set_mail_status(self.tr("ON"), ready=True)
        else:
            leap_assert(False,
                        "Don't know how to handle this state: %s"
                        % (req.event))

        if ext_status is not None:
            self._set_long_mail_status(ext_status)

    def _set_long_mail_status(self, ext_status):
        self.ui.lblLongMailStatus.setText(ext_status)
        self.ui.grpMailStatus.setVisible(len(ext_status) > 0)

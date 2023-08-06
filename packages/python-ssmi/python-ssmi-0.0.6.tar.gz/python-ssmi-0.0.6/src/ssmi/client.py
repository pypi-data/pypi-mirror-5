# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2009, 2010, 2011 Praekelt Foundation <dev@praekeltfoundation.org>
# BSD - see LICENSE for details

"""Python module for SSMI protocol to send/receive USSD and SMS."""

# Imports

from types import StringTypes

from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, protocol
from twisted.python import log
from twisted.python.failure import Failure

from ssmi.errors import SSMIRemoteServerError

# Constants

LINKCHECK_PERIOD = 60.0

SSMI_HEADER = "SSMI"

SSMI_SEND_LOGIN = "1"
SSMI_SEND_SMS = "2"
SSMI_SEND_LINK_CHECK = "3"
SSMI_SEND_BINARY = "4"
SSMI_SEND_LOGOUT = "99"
SSMI_SEND_USSD = "110"
SSMI_SEND_WAP_PUSH = "112"

SSMI_RESPONSE_SEQ = "100"
SSMI_RESPONSE_ACK = "101"
SSMI_RESPONSE_NACK = "102"
SSMI_RESPONSE_TEXT_MESSAGE = "103"
SSMI_RESPONSE_DELIVERY_MESSAGE = "104"
SSMI_RESPONSE_FREEFORM_MESSAGE = "105"
SSMI_RESPONSE_BINARY_MESSAGE = "106"
SSMI_RESPONSE_PREMIUMRATED_MESSAGE = "107"
SSMI_RESPONSE_BINARY_PREMIUMRATED_MESSAGE = "108"
SSMI_RESPONSE_USSD = "110"
SSMI_RESPONSE_USSD_EXTENDED = "111"
SSMI_RESPONSE_EXTENDED_RETURN = "113"
SSMI_RESPONSE_EXTENDED_RETURN_BINARY = "116"
SSMI_RESPONSE_EXTENDED_PREMIUMRATED_MESSAGE = "117"
SSMI_RESPONSE_EXTENDED_BINARY_PREMIUMRATED_MESSAGE = "118"
SSMI_RESPONSE_REMOTE_LOGOUT = "199"

SSMI_USSD_TYPE_NEW = "1"
SSMI_USSD_TYPE_EXISTING = "2"
SSMI_USSD_TYPE_END = "3"
SSMI_USSD_TYPE_TIMEOUT = "4"
SSMI_USSD_TYPE_REDIRECT = "5"
SSMI_USSD_TYPE_NI = "6"

ack_reason = {
    "1": "Login OK",
    "2": "Link check response",
}

nack_reason = {
    "1": "Invalid username/password combination",
    "2": "Invalid/unknown message type",
    "3": "Could not parse message",
    "4": "Account suspended (non-payment or abuse)",
}

# global status

DEBUG = False


def set_debug(debug):
    """Set global DEBUG flag."""
    global DEBUG
    if debug:
        DEBUG = True


class SSMIClient(LineReceiver):
    """Client for SSMI"""

    delimiter = '\r'
    encoding = 'utf-8'

    def __init__(self, app_register_callback=None):
        """init SSMIClient.

        app_register_callback: lambda: callback for setup
          -- this callback should call back again to
             self.app_setup to set username, password,
             and other callbacks.
        """
        self._link_check_pending = 0
        if app_register_callback is not None:
            # register protocol with app
            app_register_callback(self)

    def app_setup(self, username, password, ussd_callback=None,
                  sms_callback=None, errback=None, link_check_period=None):
        """Set up application callbacks to handle receiving USSD or SMS.

        username: string -- username for SSMI service
        password: string -- password for SSMI service
        ussd_callback: lambda -- callback for data received
        sms_callback: lambda -- callback for SMS received
        errback: lambda -- callback for error handling
        linkcheck_period -- number of seconds between link checks
        """
        if link_check_period is None:
            link_check_period = LINKCHECK_PERIOD
        self._username = username
        self._password = password
        self._ussd_callback = ussd_callback
        self._sms_callback = sms_callback
        self._errback = errback  # WHUI
        self._link_check_period = link_check_period
        if DEBUG:
            log.msg('SSMIClient app_setup done')

    def connectionMade(self):
        """Handle connection establishment

        Log in
        """
        if DEBUG:
            log.msg('SSMIClient logging in')
        self.sendLine("%s,%s,%s,%s" % (SSMI_HEADER,
                                       SSMI_SEND_LOGIN,
                                       self._username,
                                       self._password))
        self.updateCall = reactor.callLater(self._link_check_period,
                                            self.linkcheck)

    def linkcheck(self):
        if DEBUG:
            log.msg("SSMIClient linkcheck")
        self.updateCall = None
        if self._link_check_pending == 2:
            log.msg('SSMIClient Link check not acked 2 times, disconnecting')
            self.transport.loseConnection()
            return
        self.sendLine("%s,%s" % (SSMI_HEADER,
                                 SSMI_SEND_LINK_CHECK))
        self._link_check_pending = self._link_check_pending + 1
        self.updateCall = reactor.callLater(self._link_check_period,
                                            self.linkcheck)

    def parseGenfield(self, genfield):
        genarray = genfield.split(":")
        # pad the array to ensure enough elements
        # in theory we should have the five sub-params listed below
        # but in practice we may get '::::' (empty values)
        # or even '::' (less than 5 values)
        genarray += ['', '', '', '', '']
        genfields = {
            'IMSI': genarray[0],
            'Subscriber type': genarray[1],
            'OperatorID': genarray[2],
            'SessionID': genarray[3],
            'ValiPort': genarray[4],
        }
        return genfields

    def lineReceived(self, data):
        log.msg("SSMIClient RECV USSD: %s" % data)
        response = data.split(',')
        if not response[0] == SSMI_HEADER:
            # logging the error is enough -- linkcheck will close
            # the transport if the connection is completely broken
            log.err(Failure(SSMIRemoteServerError(
                'No SSMI header. Skipping bad line %r' % data)))
            return
        response_code = response[1]
        if response_code == SSMI_RESPONSE_ACK:
            reason = response[2]
            if DEBUG:
                log.msg('SSMIClient ACK %s' % ack_reason[reason])
            if reason == "2":
                # Link check acked
                self._link_check_pending = 0
        elif response_code == SSMI_RESPONSE_NACK:
            reason = response[2]
            log.msg('SSMIClient NACK %s' % nack_reason[reason])
        elif response_code == SSMI_RESPONSE_USSD:
            msisdn, ussd_type, phase = response[2:5]
            message = ",".join(response[5:])
            if ussd_type == SSMI_USSD_TYPE_NEW:
                if DEBUG:
                    log.msg('SSMIClient New session')
            elif ussd_type == SSMI_USSD_TYPE_EXISTING:
                if DEBUG:
                    log.msg('SSMIClient Existing session')
            elif ussd_type == SSMI_USSD_TYPE_END:
                log.msg('SSMIClient End of session')
            elif ussd_type == SSMI_USSD_TYPE_TIMEOUT:
                log.msg('SSMIClient TIMEOUT')
            # Call a callback into the app with the message.
            if self._ussd_callback is not None:
                self._ussd_callback(msisdn, ussd_type, phase, message)

        elif response_code == SSMI_RESPONSE_USSD_EXTENDED:
            msisdn, ussd_type, phase, genfield = response[2:6]
            message = ",".join(response[6:])
            if ussd_type == SSMI_USSD_TYPE_NEW:
                if DEBUG:
                    log.msg('SSMIClient New session')
            elif ussd_type == SSMI_USSD_TYPE_EXISTING:
                if DEBUG:
                    log.msg('SSMIClient Existing session')
            elif ussd_type == SSMI_USSD_TYPE_END:
                log.msg('SSMIClient End of session')
            elif ussd_type == SSMI_USSD_TYPE_TIMEOUT:
                log.msg('SSMIClient TIMEOUT')
            # Call a callback into the app with the message.
            if self._ussd_callback is not None:
                self._ussd_callback(msisdn, ussd_type, phase, message,
                                    self.parseGenfield(genfield))

        #elif response_code == SSMI_RESPONSE_TEXT_MESSAGE
        #elif response_code == SSMI_RESPONSE_DELIVERY_MESSAGE
        #elif response_code == SSMI_RESPONSE_SEQ
        elif response_code == SSMI_RESPONSE_REMOTE_LOGOUT:
            ip = response[2]
            log.msg(
                'SSMIClient REMOTE LOGOUT RECEIVED. Other IP address: %s' % ip)
            self.transport.loseConnection()

# SSMI_RESPONSE_SEQ = "100"
# SSMI_RESPONSE_TEXT_MESSAGE = "103"
# SSMI_RESPONSE_DELIVERY_MESSAGE = "104"
# SSMI_RESPONSE_FREEFORM_MESSAGE = "105"
# SSMI_RESPONSE_BINARY_MESSAGE = "106"
# SSMI_RESPONSE_PREMIUMRATED_MESSAGE = "107"
# SSMI_RESPONSE_BINARY_PREMIUMRATED_MESSAGE = "108"
# SSMI_RESPONSE_USSD_EXTENDED = "111"
# SSMI_RESPONSE_EXTENDED_RETURN = "113"
# SSMI_RESPONSE_EXTENDED_RETURN_BINARY = "116"
# SSMI_RESPONSE_EXTENDED_PREMIUMRATED_MESSAGE = "117"
# SSMI_RESPONSE_EXTENDED_BINARY_PREMIUMRATED_MESSAGE = "118"

    def connectionLost(self, reason):
        if self.updateCall:
            self.updateCall.cancel()
        self.updateCall = None
        log.msg("SSMIClient Connection lost: %s" % reason)

    def send_ussd(self, msisdn, message, ussd_type=SSMI_USSD_TYPE_EXISTING):
        """Send USSD.

        msisdn: string -- cellphone number of recipient
        message: string -- message content
        ussd_type: type of SSMI reply
        """
        if ussd_type not in [SSMI_USSD_TYPE_EXISTING, SSMI_USSD_TYPE_END,
                             SSMI_USSD_TYPE_REDIRECT, SSMI_USSD_TYPE_NI]:
            log.msg('SSMIClient send_ussd bad ussd_type: %r' % ussd_type)
            return
        if not type(message) in StringTypes:
            log.msg('SSMIClient send_ussd bad message type: %r' % message)
            return
        data = "%s,%s,%s,%s,%s" % (SSMI_HEADER, SSMI_SEND_USSD, msisdn,
                                   ussd_type, message.encode(self.encoding))
        self.sendLine(data)
        log.msg('SSMIClient SEND USSD: %s' % '_'.join(data.split('\n')))

    def send_sms(self, msisdn, message, validity=0):
        """Send SMS.

        msisdn: string -- cellphone number of recipient
        message: string(160) -- message content
        validity: integer -- validity in minutes, default 0 for a week
        """
        data = "%s,%s,%s,%s,%s" % (SSMI_HEADER, SSMI_SEND_SMS,
                                   str(validity), str(msisdn), str(message))
        self.sendLine(data)
        log.msg('SSMIClient SEND SMS: %s' % data)

    def send_wap_push(self, msisdn, subject, url):
        """Send a WAP Push.

        msisdn: string -- cellphone number of recipient
        subject: string -- subject displayed to subscriber
        url: string -- url to be sent to subscriber
        """
        data = "%s,%s,%s,%s,%s" % (SSMI_HEADER, SSMI_SEND_WAP_PUSH,
                                   str(msisdn), str(subject), str(url))
        self.sendLine(data)
        log.msg('SSMIClient SEND WAP PUSH: %s' % data)


class SSMIFactory(protocol.ReconnectingClientFactory):
    def __init__(self, app_register_callback=None):
        """init SSMIFactory.

        app_register_callback: lambda: callback for setup
        """
        self._app_register_callback = app_register_callback

    def startConnecting(self, connector):
        if DEBUG:
            log.msg('SSMIFactory Started to connect.')

    def buildProtocol(self, addr):
        if DEBUG:
            log.msg('SSMIFactory Connected.')
            log.msg('SSMIFactory Resetting reconnection delay')
        self.resetDelay()
        return SSMIClient(app_register_callback=self._app_register_callback)

    def clientConnectionFailed(self, connector, reason):
        log.msg("SSMIFactory Connection failed: %s" % reason)
        protocol.ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        log.msg("SSMIFactory Connection lost: %s" % reason)
        protocol.ReconnectingClientFactory.clientConnectionLost(
            self, connector, reason)

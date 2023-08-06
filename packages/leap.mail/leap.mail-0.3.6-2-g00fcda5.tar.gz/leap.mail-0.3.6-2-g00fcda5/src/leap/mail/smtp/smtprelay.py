# -*- coding: utf-8 -*-
# smtprelay.py
# Copyright (C) 2013 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
LEAP SMTP encrypted relay.

The following classes comprise the SMTP relay service:

    * SMTPFactory - A twisted.internet.protocol.ServerFactory that provides
      the SMTPDelivery protocol.
    * SMTPDelivery - A twisted.mail.smtp.IMessageDelivery implementation. It
      knows how to validate sender and receiver of messages and it generates
      an EncryptedMessage for each recipient.
    * SSLContextFactory - Contains the relevant ssl information for the
      connection.
    * EncryptedMessage - An implementation of twisted.mail.smtp.IMessage that
      knows how to encrypt/sign itself before sending.


"""

import re
from StringIO import StringIO
from email.Header import Header
from email.utils import parseaddr
from email.parser import Parser
from email.mime.application import MIMEApplication

from zope.interface import implements
from OpenSSL import SSL
from twisted.mail import smtp
from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor, ssl
from twisted.internet import defer
from twisted.python import log

from leap.common.check import leap_assert, leap_assert_type
from leap.common.events import proto, signal
from leap.keymanager import KeyManager
from leap.keymanager.openpgp import OpenPGPKey
from leap.keymanager.errors import KeyNotFound
from leap.mail.smtp.rfc3156 import (
    MultipartSigned,
    MultipartEncrypted,
    PGPEncrypted,
    PGPSignature,
    RFC3156CompliantGenerator,
    encode_base64_rec,
)

# replace email generator with a RFC 3156 compliant one.
from email import generator
generator.Generator = RFC3156CompliantGenerator


#
# Exceptions
#

class MalformedConfig(Exception):
    """
    Raised when the configuration dictionary passed as parameter is malformed.
    """
    pass


#
# Helper utilities
#

HOST_KEY = 'host'
PORT_KEY = 'port'
CERT_KEY = 'cert'
KEY_KEY = 'key'
ENCRYPTED_ONLY_KEY = 'encrypted_only'


def assert_config_structure(config):
    """
    Assert that C{config} is a dict with the following structure:

        {
            HOST_KEY: '<str>',
            PORT_KEY: <int>,
            CERT_KEY: '<str>',
            KEY_KEY: '<str>',
            ENCRYPTED_ONLY_KEY: <bool>,
        }

    @param config: The dictionary to check.
    @type config: dict
    """
    # assert smtp config structure is valid
    leap_assert_type(config, dict)
    leap_assert(HOST_KEY in config)
    leap_assert_type(config[HOST_KEY], str)
    leap_assert(PORT_KEY in config)
    leap_assert_type(config[PORT_KEY], int)
    leap_assert(CERT_KEY in config)
    leap_assert_type(config[CERT_KEY], (str, unicode))
    leap_assert(KEY_KEY in config)
    leap_assert_type(config[KEY_KEY], (str, unicode))
    leap_assert(ENCRYPTED_ONLY_KEY in config)
    leap_assert_type(config[ENCRYPTED_ONLY_KEY], bool)
    # assert received params are not empty
    leap_assert(config[HOST_KEY] != '')
    leap_assert(config[PORT_KEY] is not 0)
    leap_assert(config[CERT_KEY] != '')
    leap_assert(config[KEY_KEY] != '')


def validate_address(address):
    """
    Validate C{address} as defined in RFC 2822.

    @param address: The address to be validated.
    @type address: str

    @return: A valid address.
    @rtype: str

    @raise smtp.SMTPBadRcpt: Raised if C{address} is invalid.
    """
    leap_assert_type(address, str)
    # in the following, the address is parsed as described in RFC 2822 and
    # ('', '') is returned if the parse fails.
    _, address = parseaddr(address)
    if address == '':
        raise smtp.SMTPBadRcpt(address)
    return address


#
# SMTPFactory
#

class SMTPFactory(ServerFactory):
    """
    Factory for an SMTP server with encrypted relaying capabilities.
    """

    def __init__(self, keymanager, config):
        """
        Initialize the SMTP factory.

        @param keymanager: A KeyManager for retrieving recipient's keys.
        @type keymanager: leap.common.keymanager.KeyManager
        @param config: A dictionary with smtp configuration. Should have
            the following structure:
                {
                    HOST_KEY: '<str>',
                    PORT_KEY: <int>,
                    CERT_KEY: '<str>',
                    KEY_KEY: '<str>',
                    ENCRYPTED_ONLY_KEY: <bool>,
                }
        @type config: dict
        """
        # assert params
        leap_assert_type(keymanager, KeyManager)
        assert_config_structure(config)
        # and store them
        self._km = keymanager
        self._config = config

    def buildProtocol(self, addr):
        """
        Return a protocol suitable for the job.

        @param addr: An address, e.g. a TCP (host, port).
        @type addr:  twisted.internet.interfaces.IAddress

        @return: The protocol.
        @rtype: SMTPDelivery
        """
        smtpProtocol = smtp.SMTP(SMTPDelivery(self._km, self._config))
        smtpProtocol.factory = self
        return smtpProtocol


#
# SMTPDelivery
#

class SMTPDelivery(object):
    """
    Validate email addresses and handle message delivery.
    """

    implements(smtp.IMessageDelivery)

    def __init__(self, keymanager, config):
        """
        Initialize the SMTP delivery object.

        @param keymanager: A KeyManager for retrieving recipient's keys.
        @type keymanager: leap.common.keymanager.KeyManager
        @param config: A dictionary with smtp configuration. Should have
            the following structure:
                {
                    HOST_KEY: '<str>',
                    PORT_KEY: <int>,
                    CERT_KEY: '<str>',
                    KEY_KEY: '<str>',
                    ENCRYPTED_ONLY_KEY: <bool>,
                }
        @type config: dict
        """
        # assert params
        leap_assert_type(keymanager, KeyManager)
        assert_config_structure(config)
        # and store them
        self._km = keymanager
        self._config = config
        self._origin = None

    def receivedHeader(self, helo, origin, recipients):
        """
        Generate the 'Received:' header for a message.

        @param helo: The argument to the HELO command and the client's IP
            address.
        @type helo: (str, str)
        @param origin: The address the message is from.
        @type origin: twisted.mail.smtp.Address
        @param recipients: A list of the addresses for which this message is
            bound.
        @type: list of twisted.mail.smtp.User

        @return: The full "Received" header string.
        @type: str
        """
        myHostname, clientIP = helo
        headerValue = "by %s from %s with ESMTP ; %s" % (
            myHostname, clientIP, smtp.rfc822date())
        # email.Header.Header used for automatic wrapping of long lines
        return "Received: %s" % Header(headerValue)

    def validateTo(self, user):
        """
        Validate the address of C{user}, a recipient of the message.

        This method is called once for each recipient and validates the
        C{user}'s address against the RFC 2822 definition. If the
        configuration option ENCRYPTED_ONLY_KEY is True, it also asserts the
        existence of the user's key.

        In the end, it returns an encrypted message object that is able to
        send itself to the C{user}'s address.

        @param user: The user whose address we wish to validate.
        @type: twisted.mail.smtp.User

        @return: A Deferred which becomes, or a callable which takes no
            arguments and returns an object implementing IMessage. This will
            be called and the returned object used to deliver the message when
            it arrives.
        @rtype: no-argument callable

        @raise SMTPBadRcpt: Raised if messages to the address are not to be
            accepted.
        """
        # try to find recipient's public key
        try:
            address = validate_address(user.dest.addrstr)
            pubkey = self._km.get_key(address, OpenPGPKey)
            log.msg("Accepting mail for %s..." % user.dest.addrstr)
            signal(proto.SMTP_RECIPIENT_ACCEPTED_ENCRYPTED, user.dest.addrstr)
        except KeyNotFound:
            # if key was not found, check config to see if will send anyway.
            if self._config[ENCRYPTED_ONLY_KEY]:
                signal(proto.SMTP_RECIPIENT_REJECTED, user.dest.addrstr)
                raise smtp.SMTPBadRcpt(user.dest.addrstr)
            log.msg("Warning: will send an unencrypted message (because "
                    "encrypted_only' is set to False).")
            signal(
                proto.SMTP_RECIPIENT_ACCEPTED_UNENCRYPTED, user.dest.addrstr)
        return lambda: EncryptedMessage(
            self._origin, user, self._km, self._config)

    def validateFrom(self, helo, origin):
        """
        Validate the address from which the message originates.

        @param helo: The argument to the HELO command and the client's IP
            address.
        @type: (str, str)
        @param origin: The address the message is from.
        @type origin: twisted.mail.smtp.Address

        @return: origin or a Deferred whose callback will be passed origin.
        @rtype: Deferred or Address

        @raise twisted.mail.smtp.SMTPBadSender: Raised if messages from this
            address are not to be accepted.
        """
        # accept mail from anywhere. To reject an address, raise
        # smtp.SMTPBadSender here.
        self._origin = origin
        return origin


#
# EncryptedMessage
#

class SSLContextFactory(ssl.ClientContextFactory):
    def __init__(self, cert, key):
        self.cert = cert
        self.key = key

    def getContext(self):
        self.method = SSL.TLSv1_METHOD  # SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file(self.cert)
        ctx.use_privatekey_file(self.key)
        return ctx


def move_headers(origmsg, newmsg):
    headers = origmsg.items()
    unwanted_headers = ['content-type', 'mime-version', 'content-disposition',
                        'content-transfer-encoding']
    headers = filter(lambda x: x[0].lower() not in unwanted_headers, headers)
    for hkey, hval in headers:
        newmsg.add_header(hkey, hval)
        del(origmsg[hkey])


class EncryptedMessage(object):
    """
    Receive plaintext from client, encrypt it and send message to a
    recipient.
    """
    implements(smtp.IMessage)

    def __init__(self, fromAddress, user, keymanager, config):
        """
        Initialize the encrypted message.

        @param fromAddress: The address of the sender.
        @type fromAddress: twisted.mail.smtp.Address
        @param user: The recipient of this message.
        @type user: twisted.mail.smtp.User
        @param keymanager: A KeyManager for retrieving recipient's keys.
        @type keymanager: leap.common.keymanager.KeyManager
        @param config: A dictionary with smtp configuration. Should have
            the following structure:
                {
                    HOST_KEY: '<str>',
                    PORT_KEY: <int>,
                    CERT_KEY: '<str>',
                    KEY_KEY: '<str>',
                    ENCRYPTED_ONLY_KEY: <bool>,
                }
        @type config: dict
        """
        # assert params
        leap_assert_type(user, smtp.User)
        leap_assert_type(keymanager, KeyManager)
        assert_config_structure(config)
        # and store them
        self._fromAddress = fromAddress
        self._user = user
        self._km = keymanager
        self._config = config
        # initialize list for message's lines
        self.lines = []

    #
    # methods from smtp.IMessage
    #

    def lineReceived(self, line):
        """
        Handle another line.

        @param line: The received line.
        @type line: str
        """
        self.lines.append(line)

    def eomReceived(self):
        """
        Handle end of message.

        This method will encrypt and send the message.
        """
        log.msg("Message data complete.")
        self.lines.append('')  # add a trailing newline
        try:
            self._maybe_encrypt_and_sign()
            return self.sendMessage()
        except KeyNotFound:
            return None

    def parseMessage(self):
        """
        Separate message headers from body.
        """
        parser = Parser()
        return parser.parsestr('\r\n'.join(self.lines))

    def connectionLost(self):
        """
        Log an error when the connection is lost.
        """
        log.msg("Connection lost unexpectedly!")
        log.err()
        signal(proto.SMTP_CONNECTION_LOST, self._user.dest.addrstr)
        # unexpected loss of connection; don't save
        self.lines = []

    def sendSuccess(self, r):
        """
        Callback for a successful send.

        @param r: The result from the last previous callback in the chain.
        @type r: anything
        """
        log.msg(r)
        signal(proto.SMTP_SEND_MESSAGE_SUCCESS, self._user.dest.addrstr)

    def sendError(self, e):
        """
        Callback for an unsuccessfull send.

        @param e: The result from the last errback.
        @type e: anything
        """
        log.msg(e)
        log.err()
        signal(proto.SMTP_SEND_MESSAGE_ERROR, self._user.dest.addrstr)

    def sendMessage(self):
        """
        Send the message.

        This method will prepare the message (headers and possibly encrypted
        body) and send it using the ESMTPSenderFactory.

        @return: A deferred with callbacks for error and success of this
            message send.
        @rtype: twisted.internet.defer.Deferred
        """
        msg = self._msg.as_string(False)

        log.msg("Connecting to SMTP server %s:%s" % (self._config[HOST_KEY],
                                                     self._config[PORT_KEY]))

        d = defer.Deferred()
        # we don't pass an ssl context factory to the ESMTPSenderFactory
        # because ssl will be handled by reactor.connectSSL() below.
        factory = smtp.ESMTPSenderFactory(
            "",  # username is blank because server does not use auth.
            "",  # password is blank because server does not use auth.
            self._fromAddress.addrstr,
            self._user.dest.addrstr,
            StringIO(msg),
            d,
            requireAuthentication=False,
            requireTransportSecurity=True)
        signal(proto.SMTP_SEND_MESSAGE_START, self._user.dest.addrstr)
        reactor.connectSSL(
            self._config[HOST_KEY],
            self._config[PORT_KEY],
            factory,
            contextFactory=SSLContextFactory(self._config[CERT_KEY],
                                             self._config[KEY_KEY]))
        d.addCallback(self.sendSuccess)
        d.addErrback(self.sendError)
        return d

    #
    # encryption methods
    #

    def _encrypt_and_sign(self, pubkey, signkey):
        """
        Create an RFC 3156 compliang PGP encrypted and signed message using
        C{pubkey} to encrypt and C{signkey} to sign.

        @param pubkey: The public key used to encrypt the message.
        @type pubkey: leap.common.keymanager.openpgp.OpenPGPKey
        @param signkey: The private key used to sign the message.
        @type signkey: leap.common.keymanager.openpgp.OpenPGPKey
        """
        # parse original message from received lines
        origmsg = self.parseMessage()
        # create new multipart/encrypted message with 'pgp-encrypted' protocol
        newmsg = MultipartEncrypted('application/pgp-encrypted')
        # move (almost) all headers from original message to the new message
        move_headers(origmsg, newmsg)
        # create 'application/octet-stream' encrypted message
        encmsg = MIMEApplication(
            self._km.encrypt(origmsg.as_string(unixfrom=False), pubkey,
                             sign=signkey),
            _subtype='octet-stream', _encoder=lambda x: x)
        encmsg.add_header('content-disposition', 'attachment',
                          filename='msg.asc')
        # create meta message
        metamsg = PGPEncrypted()
        metamsg.add_header('Content-Disposition', 'attachment')
        # attach pgp message parts to new message
        newmsg.attach(metamsg)
        newmsg.attach(encmsg)
        self._msg = newmsg

    def _sign(self, signkey):
        """
        Create an RFC 3156 compliant PGP signed MIME message using C{signkey}.

        @param signkey: The private key used to sign the message.
        @type signkey: leap.common.keymanager.openpgp.OpenPGPKey
        """
        # parse original message from received lines
        origmsg = self.parseMessage()
        # create new multipart/signed message
        newmsg = MultipartSigned('application/pgp-signature', 'pgp-sha512')
        # move (almost) all headers from original message to the new message
        move_headers(origmsg, newmsg)
        # apply base64 content-transfer-encoding
        encode_base64_rec(origmsg)
        # get message text with headers and replace \n for \r\n
        fp = StringIO()
        g = RFC3156CompliantGenerator(
            fp, mangle_from_=False, maxheaderlen=76)
        g.flatten(origmsg)
        msgtext = re.sub('\r?\n', '\r\n', fp.getvalue())
        # make sure signed message ends with \r\n as per OpenPGP stantard.
        if origmsg.is_multipart():
            if not msgtext.endswith("\r\n"):
                msgtext += "\r\n"
        # calculate signature
        signature = self._km.sign(msgtext, signkey, digest_algo='SHA512',
                                  clearsign=False, detach=True, binary=False)
        sigmsg = PGPSignature(signature)
        # attach original message and signature to new message
        newmsg.attach(origmsg)
        newmsg.attach(sigmsg)
        self._msg = newmsg

    def _maybe_encrypt_and_sign(self):
        """
        Encrypt the message body.

        Fetch the recipient key and encrypt the content to the
        recipient. If a key is not found, then the behaviour depends on the
        configuration parameter ENCRYPTED_ONLY_KEY. If it is False, the message
        is sent unencrypted and a warning is logged. If it is True, the
        encryption fails with a KeyNotFound exception.

        @raise KeyNotFound: Raised when the recipient key was not found and
            the ENCRYPTED_ONLY_KEY configuration parameter is set to True.
        """
        from_address = validate_address(self._fromAddress.addrstr)
        signkey = self._km.get_key(from_address, OpenPGPKey, private=True)
        log.msg("Will sign the message with %s." % signkey.fingerprint)
        to_address = validate_address(self._user.dest.addrstr)
        try:
            # try to get the recipient pubkey
            pubkey = self._km.get_key(to_address, OpenPGPKey)
            log.msg("Will encrypt the message to %s." % pubkey.fingerprint)
            signal(proto.SMTP_START_ENCRYPT_AND_SIGN,
                   "%s,%s" % (self._fromAddress.addrstr, to_address))
            self._encrypt_and_sign(pubkey, signkey)
            signal(proto.SMTP_END_ENCRYPT_AND_SIGN,
                   "%s,%s" % (self._fromAddress.addrstr, to_address))
        except KeyNotFound:
            # at this point we _can_ send unencrypted mail, because if the
            # configuration said the opposite the address would have been
            # rejected in SMTPDelivery.validateTo().
            log.msg('Will send unencrypted message to %s.' % to_address)
            signal(proto.SMTP_START_SIGN, self._fromAddress.addrstr)
            self._sign(signkey)
            signal(proto.SMTP_END_SIGN, self._fromAddress.addrstr)

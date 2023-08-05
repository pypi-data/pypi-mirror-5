# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Aurelien Bompard <abompard@fedoraproject.org>
Author: Aurelien Bompard <abompard@fedoraproject.org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at
your option) any later version.
See http://www.gnu.org/copyleft/gpl.html  for the full text of the
license.
"""

import datetime

from zope.interface import implements
from storm.locals import Unicode, RawStr, Int, ReferenceSet, Reference, Proxy
from storm.locals import Storm
from storm.expr import Desc
from mailman.interfaces.messages import IMessage

from kittystore.utils import get_message_id_hash
from .hack_datetime import DateTime

# pylint: disable-msg=R0902,R0913,R0903
# R0902: Too many instance attributes (X/7)
# R0913: Too many arguments (X/5)
# R0903: Too few public methods (X/2)


__all__ = ("List", "Email", "Attachment")


class List(Storm):
    # The 'List' name is part of storm's locals
    # pylint: disable-msg=E0102
    """
    An archived mailing-list.

    Not strictly necessary yet since the list name is used in the email table,
    but at some point we'll want to store more information on lists in the
    database.
    """

    __storm_table__ = "list"

    name = Unicode(primary=True)
    display_name = Unicode()
    subject_prefix = Unicode()

    def __init__(self, name):
        self.name = unicode(name)


class Email(Storm):
    """
    An archived email, from a mailing-list. It is identified by both the list
    name and the message id.
    """

    implements(IMessage)
    __storm_table__ = "email"
    __storm_primary__ = "list_name", "message_id"

    list_name = Unicode()
    message_id = Unicode()
    sender_name = Unicode()
    sender_email = Unicode()
    subject = Unicode()
    content = Unicode()
    date = DateTime()
    timezone = Int()
    in_reply_to = Unicode()
    message_id_hash = Unicode()
    thread_id = Unicode()
    archived_date = DateTime(default_factory=datetime.datetime.now)
    thread_depth = Int(default=0)
    thread_order = Int(default=0)
    # path is required by IMessage, but it makes no sense here
    path = None
    # References
    attachments = ReferenceSet(
                    (list_name,
                     message_id),
                    ("Attachment.list_name",
                     "Attachment.message_id"),
                    order_by="Attachment.counter"
                    )
    thread = Reference((list_name, thread_id),
                       ("Thread.list_name", "Thread.thread_id"))
    full_email = Reference((list_name, message_id),
                     ("EmailFull.list_name", "EmailFull.message_id"))
    full = Proxy(full_email, "EmailFull.full")

    def __init__(self, list_name, message_id):
        self.list_name = unicode(list_name)
        self.message_id = unicode(message_id)
        self.message_id_hash = unicode(get_message_id_hash(self.message_id))


class EmailFull(Storm):
    """
    The full contents of an archived email, for storage and post-processing
    reasons.
    """
    __storm_table__ = "email_full"
    __storm_primary__ = "list_name", "message_id"

    list_name = Unicode()
    message_id = Unicode()
    full = RawStr()
    email = Reference((list_name, message_id),
                     ("Email.list_name", "Email.message_id"))

    def __init__(self, list_name, message_id, full):
        self.list_name = unicode(list_name)
        self.message_id = unicode(message_id)
        self.full = full


class Attachment(Storm):

    __storm_table__ = "attachment"
    __storm_primary__ = "list_name", "message_id", "counter"

    list_name = Unicode()
    message_id = Unicode()
    counter = Int()
    name = Unicode()
    content_type = Unicode()
    encoding = Unicode()
    size = Int()
    content = RawStr()
    # reference to the email
    email = Reference((list_name, message_id),
                      (Email.list_name, Email.message_id))


class Thread(Storm):
    """
    A thread of archived email, from a mailing-list. It is identified by both
    the list name and the thread id.
    """

    __storm_table__ = "thread"
    __storm_primary__ = "list_name", "thread_id"

    list_name = Unicode()
    thread_id = Unicode()
    date_active = DateTime()
    emails = ReferenceSet(
                (list_name, thread_id),
                (Email.list_name, Email.thread_id),
                order_by=Email.date
             )
    emails_by_reply = ReferenceSet(
                (list_name, thread_id),
                (Email.list_name, Email.thread_id),
                order_by=Email.thread_order
             )
    _starting_email = None

    def __init__(self, list_name, thread_id, date_active=None):
        self.list_name = unicode(list_name)
        self.thread_id = unicode(thread_id)
        self.date_active = date_active

    @property
    def _starting_email_req(self):
        """ Returns the request to get the starting email.
        If there are no results with in_reply_to IS NULL, then it's
        probably a partial import and we don't have the real first email.
        In this case, use the date.
        """
        return self.emails.order_by(Email.in_reply_to != None, Email.date)

    @property
    def starting_email(self):
        """Return (and cache) the email starting this thread"""
        if self._starting_email is None:
            self._starting_email = self._starting_email_req.first()
        return self._starting_email

    @property
    def last_email(self):
        return self.emails.order_by(Desc(Email.date)).first()

    @property
    def subject(self):
        """Return the subject of this thread"""
        if self._starting_email is not None:
            return self.starting_email.subject
        else:
            # Don't get the whole message if it's not cached yet (useful for
            # HyperKitty's thread view).
            return self._starting_email_req.values(Email.subject).next()

    @property
    def participants(self):
        """Set of email senders in this thread"""
        p = []
        for sender in self.emails.find().config(distinct=True
                        ).order_by().values(Email.sender_name, Email.sender_email):
            p.append(sender)
        return p

    @property
    def email_ids(self):
        return list(self.emails.find().order_by().values(Email.message_id))

    @property
    def email_id_hashes(self):
        return list(self.emails.find().order_by().values(Email.message_id_hash))

    def __len__(self):
        return self.emails.count()

    def __storm_pre_flush__(self):
        """Auto-set the active date from the last email in thread"""
        if self.date_active is not None:
            return
        email_dates = list(self.emails.order_by(Desc(Email.date)
                                ).config(limit=1).values(Email.date))
        if email_dates:
            self.date_active = email_dates[0]
        else:
            self.date_active = datetime.datetime.now()

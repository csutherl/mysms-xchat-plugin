__module_name__ = "MySms Integration"
__module_version__ = "1.0.0"
__module_description__ = "MySms Integration by Coty"
__module_author__ = "coty"

#
#    Adding this to solve the namespace issue
#    This line adds the current dirname to the pythonpath
#
import sys
import os

path = os.path.dirname(__file__)
if not path in sys.path:
    sys.path.append(path)
# end

print "\0034" + __module_name__ + " " + __module_version__ + " has been loaded\003"

from settings import mysms_config, console
from mysmsclient import MySmsClient

try:
    import xchat
except ImportError:
    print "Error loading xchat module."

import re
import logging
from settings import get_max_id, persist_max_id


class XChatClient():
    __mysms = MySmsClient()
    __contexts = {}  # array to store contexts keyed on the contact name

    def __init__(self):
        # setup logging
        self.log = logging.getLogger(name='xchatclient')
        self.log.setLevel(mysms_config['logging_level'])
        self.log.addHandler(console)

        # add hooks
        self.add_hooks()

    # TODO: Add use case to stop messages for current context instead of specifying contact.
    def handle_stop(self, raw_contact):
        # added substring replacement for space to
        self.log.debug("Removing %s from contacts." % raw_contact)

        self.remove_from_contexts(re.sub(' ', '_', raw_contact))

    # TODO: Handle regular numbers without the +1, assuming US.
    # TODO: Potential TODO anyway...add setting to config file for default country code and/or area code
    def open_dialog(self, raw_contact):
        try:
            # added substring replacement for space to _
            name_without_spaces = re.sub(' ', '_', raw_contact)
            contact = self.__mysms.verifyContact(name_without_spaces)

            self.log.debug("Attempting to open dialog with %s" % contact)

            if re.match('^[+]\d{11}', contact) is not None:
                contact_name = self.__mysms.getContactName(contact)
            else:
                contact_name = contact

            self.log.debug("Opening dialog with %s" % contact_name)

            # surround with quotes in case the contact name has spaces
            xchat.command("query \"%s\"" % contact_name)

        except KeyError:
            like_contacts = self.__mysms.getLikeContact(name_without_spaces)

            if len(like_contacts) is not 0:
                # if the contact does not exist, then we ask if its one of the like contacts
                xchat.command("echo Did you mean (case sensitive):")
                for name in like_contacts:
                    xchat.command("echo %s" % name)
            else:
                # added to produce output if name provided is not in contacts
                self.log.error("Specified name nor any names like it does not exist in your contacts list.")

    def mysms_cb(self, word, word_eol, userdata):
        if len(word) < 2:
            self.log.error("Contact name or number required.")
        if word[1].lower() == "stop":
            if len(word) < 3:
                self.log.error("Please provide a contact to stop receiving updates for.")
            else:
                self.handle_stop(word_eol[2])
        else:
            # open a dialog with the contact
            self.open_dialog(word_eol[1])

        return xchat.EAT_ALL

    def focus_tab(self, word, word_eol, userdata):
        focused_context = xchat.get_context()
        focused_channel = focused_context.get_info("channel")

        if focused_channel not in self.__contexts and focused_channel in self.__mysms.getContactByName():
            self.add_to_contexts(focused_channel, focused_context)

        return xchat.EAT_NONE

    def add_to_contexts(self, channel, context):
        self.__contexts[channel] = context
        self.log.debug("Added context %s" % channel)

    def remove_from_contexts(self, contact_name):
        try:
            del self.__contexts[contact_name]
            self.log.info("Contact %s will no longer receive updates.", contact_name)
        except KeyError:
            self.log.error("Contact %s is not receiving updates.", contact_name)

    # TODO: Complete send message logic
    def send_message_cb(self, word, word_eol, userdata):
        contact = xchat.get_info('channel')
        # FYI: "Can not deserialize instance of java.lang.String out of START_ARRAY token" error will occur if you try
        # and pass an array into JSON here, such as using word instead of word_eol.
        message = word_eol[0]

        if contact in self.__mysms.getContactByName():
            self.log.debug("Message sent to %s! Message is %s" % (contact, message))
            self.__mysms.sendText(contact, message)
        else:
            self.log.error("Cannot send message to %s" % contact)

        return xchat.EAT_ALL

    def handle_message(self, contact, message):
        context = self.__contexts[contact]
        if message['incoming']:
            # take advantage of the recv command and use it to simulate server response
            self.log.debug("Message: %s" % message)
            # "\uD83D\uDE18" breaks this...need to figure that out, but working around it for now with try/catch
            try:
                context.command("recv :%s!%s@mysms.com PRIVMSG %s :%s" % (contact, contact, xchat.get_info('nick'), message['message']))
            # TODO: Fix this...
            except UnicodeEncodeError:
                self.log.error("Cannot encode message.")

        elif not message['incoming']:  # message is not incoming
            context.command("echo %s" % message['message'])
            # print message['message']
        else:
            self.log.error("Error. Cannot determine origin or message: %s" % message)

    # when we send a message via the mysms command, then this should loop to check for messages from that contact
    def receive_message(self, contact_phone):
        contact_name = self.__mysms.getContactName(contact_phone)

        message_limit = xchat.get_prefs('text_max_lines')  # enough messages to fill scroll back buffer
        messages = self.sort_messages(self.__mysms.syncMessages(contact_phone, message_limit))  # 5)) # 5 for testing

        # retrieve from file
        curr_maxId = get_max_id(self, contact_name)  # passing self so that logging comes through the client class

        # handle max ID
        if 'maxId' in messages[0]:
            # persist to file with contact_phone for later use
            new_max = messages[0]['maxId']
            self.log.debug("Updated max ID is %s" % new_max)
            del messages[0]

        for msg in messages:
            if msg['id'] > curr_maxId or curr_maxId is None:
                self.handle_message(contact_name, msg)

        # persist new max to file...
        persist_max_id(self, contact_name, new_max)

        return xchat.EAT_ALL

    def sort_messages(self, messages):
        sorted_messages = []
        messages_with_max = {}
        sorted_message_ids = sorted(messages.iterkeys())  # list(messages)

        # get max message id and add to dict
        messages_with_max['maxId'] = max(sorted_message_ids)
        sorted_messages.append(messages_with_max)

        for msg in sorted_message_ids:
            # add id to message json
            messages[msg]['id'] = msg  # not sure we need the ID at this point...leaving it just in case.
            sorted_messages.append(messages[msg])

        return sorted_messages

    def timer_cb(self, userdata):
        channels = list(self.__contexts)
        for channel in channels:
            if xchat.find_context(channel="%s" % channel) is not None:
                # context = self.__contexts[channel]
                # this print is for testing only to ensure that we do not print to contexts other than the contact name
                # context.command("echo context:%s" % context)
                contact_phone = self.__mysms.getContactNumber(channel)

                if contact_phone is not None:
                    self.receive_message(contact_phone)

        return 1

    def add_hooks(self):
        # create a hook for the mysms command so that we can initiate messages with a person
        xchat.hook_command("mysms", self.mysms_cb, help="/mysms <contact> Opens a dialog to a mysms contact.")
        xchat.hook_command("", self.send_message_cb)

        xchat.hook_print("Focus Tab", self.focus_tab)
        xchat.hook_timer(mysms_config['receive_delay'], self.timer_cb)


if __name__ == "__main__":
    xc = XChatClient()

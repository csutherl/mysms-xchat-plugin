__module_name__ = "MySms Integration"
__module_version__ = "1.0.0" 
__module_description__ = "MySms Integration by Coty"
__module_author__ = "coty"

#
#    Adding this to solve the namespace issue
#    This line adds the current dirname to the pythonpath
#
import sys
import logging
import time
import os
import re


path = os.path.dirname(__file__)
if not path in sys.path:
    sys.path.append(path)
# end

print "\0034" + __module_name__ + " " + __module_version__ + " has been loaded\003"

from settings import mysms_config, console
from mysmsclient import MySmsClient
import xchat
# import re
import thread


class XChatClient():
    __mysms = MySmsClient()
    __contexts = {}  # array to store contexts keyed on the contact name
    __threadCount = 0

    def __init__(self):
        # setup logging
        self.log = logging.getLogger(name='xchatclient')
        self.log.setLevel(mysms_config['logging_level'])
        self.log.addHandler(console)

        # add hooks
        self.add_hooks()

    def mysms_cb(self, word, word_eol, userdata):
        if len(word) < 2:
            self.log.error("Contact name or number required.")
        if word[1] == "stop":
            if len(word) < 3:
                self.log.error("Please provide a contact to stop receiving updates for.")
            else:
                self.remove_from_contexts(word_eol[2])
        else:
            # open a dialog with the contact
            try:
                contact = self.__mysms.verifyContact(word_eol[1])

                # if re.match('^[+]\d{11}', contact) is not None:
                if re.match('^[+]\d{11}', contact) is not None:
                    contact_name = self.__mysms.getContactName(contact)
                else:
                    contact_name = contact

                # surround with quotes in case the contact name has spaces
                xchat.command("query \"%s\"" % contact_name)

                # trigger receive loop
                try:
                    # TODO: Prevent multiple threads for the same contact. Check __contexts before created thread.
                    thread.start_new_thread(self.receive_loop,
                                            (contact_name, "ReceiveThread-%d" % self.__threadCount, 10))
                except:
                    self.log.error("Unable to start a new thread!!")

            except KeyError:
                like_contacts = self.__mysms.getLikeContact(word_eol[1])

                if len(like_contacts) is not 0:
                    # if the contact does not exist, then we ask if its one of the like contacts
                    xchat.command("echo Did you mean (case sensitive):")
                    for name in like_contacts:
                        xchat.command("echo %s" % name)

        return xchat.EAT_ALL

    def receive_loop(self, contact_name, thread_name, delay):
        # increment thread count as new ones are created
        self.__threadCount += 1
        self.log.debug("Thread %s with delay of %s" % (thread_name, delay))

        # TODO: Fix whatever is causing an exception here. It crashes xchat on plugin unload...and doesnt work...
        # receive messages for person as long as theyre in the context array
        try:
            while contact_name in self.__contexts:
                time.sleep(delay)
                self.log.debug("Contact: %s __contexts: %s" % (contact_name, self.__contexts))
        except:
            self.log.error("BORK BORK BORK")

    def focus_tab(self, word, word_eol, userdata):
        focused_context = xchat.get_context()
        focused_channel = focused_context.get_info("channel")

        if focused_channel not in self.__contexts and focused_channel in self.__mysms.getContactNumbers():
            self.__contexts[focused_channel] = focused_context
            self.log.debug("Added context %s" % focused_channel)

        return xchat.EAT_NONE

    def remove_from_contexts(self, contact_name):
        try:
            del self.__contexts[contact_name]
            self.log.info("Contact %s will no longer receive updates.", contact_name)
        except KeyError:
            self.log.error("Contact %s is not receiving updates.", contact_name)

    def send_message_cb(self, word, word_eol, userdata):
        # __mysms.sendText(contact, message)

        self.log.debug(word_eol)
        return xchat.EAT_ALL

    # when we send a message via the mysms command, then this should loop to check for messages from that contact
    def receive_message(self):
        # get messages, sort them by message id, then print them to the correct context
        # if the messages havent already been printed
        # __mysms.syncMessages(phone_number, lines_of_history)

        # take advantage of the recv command and use it to simulate server response
        # xchat.command('recv :Spartacus!~italy@i.am.spartacus PRIVMSG coty :No I am Spartacus!')
        return xchat.EAT_ALL

    def add_hooks(self):
        # create a hook for the mysms command so that we can initiate messages with a person
        xchat.hook_command("mysms", self.mysms_cb, help="/mysms <contact> Opens a dialog to a mysms contact.")
        xchat.hook_command("", self.send_message_cb)

        xchat.hook_print("Focus Tab", self.focus_tab)

if __name__ == "__main__":
    xc = XChatClient()
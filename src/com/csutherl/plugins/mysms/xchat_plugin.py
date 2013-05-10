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

from mysmsclient import MySmsClient
import xchat

__mysms = MySmsClient()

def mysms_cb(word, word_eol, userdata):
    if len(word) < 2:
        print "Contact name or number required."
    else:
        # open a dialog with the contact/number
        contactExists = __mysms.verifyContact(word_eol[1])

        if contactExists:
            xchat.command("query " + word_eol[1])
        else:
            # if the contact does not exist, then we ask if its one of the like contacts
            xchat.command("echo Did you mean:")
            xchat.command("echo " + __mysms.getLikeContact(word_eol[1]))

    return xchat.EAT_ALL


def send_message_cb(word, word_eol, userdata):
    # __mysms.sendText(contact, message)

    print word_eol
    return xchat.EAT_ALL


def receive_message_cb(self):
    # __mysms.syncMessages(phone_number, lines_of_history)

    # take advantage of the recv command and use it to simulate server response
    xchat.command('recv :Spartacus!~italy@i.am.spartacus PRIVMSG #silarus :No I am Spartacus!')
    return xchat.EAT_ALL


def add_hooks():
    ''' hook into the text handling of xchat'''
    # xchat.hook_print("Channel Message",  message_cb, xchat.PRI_HIGHEST)
    # xchat.hook_print("Channel Message Hilight", message_cb, xchat.PRI_HIGHEST)
    # xchat.hook_print("Private Message", message_cb, xchat.PRI_HIGHEST)
    # xchat.hook_print("Private Message to Dialog", message_cb, xchat.PRI_HIGHEST)
    # xchat.hook_print("Message Send", message_cb, xchat.PRI_HIGHEST)
    # xchat.hook_print("Your Message", message_cb, xchat.PRI_HIGHEST)
    # xchat.hook_print("Channel Action", message_cb, xchat.PRI_HIGHEST)
    # xchat.hook_print("Channel Action Hilight", message_cb, xchat.PRI_HIGHEST)

    # create a hook for the mysms command so that we can initiate messages with a person
    xchat.hook_command("mysms", mysms_cb, help="/mysms <contact> Opens a dialog to a mysms contact.")
    # xchat.hook_command("sms", sms_cb, help="/sms <message> Sends a message to your mysms contact.")
    xchat.hook_command("", send_message_cb)

# add hooks
add_hooks()

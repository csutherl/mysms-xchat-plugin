__module_name__ = "MySms Integration"
__module_version__ = "1.0.0" 
__module_description__ = "MySms Integration by Coty"

print "\0034" + __module_name__ + " " + __module_version__ + " has been loaded\003"

import xchat


def mysms_cb(word, word_eol, userdata):
    if len(word) < 2:
        print "Contact name or number required."
    else:
        # open a dialog with the contact/number
        contactExists = check_for_contact(word_eol[1])

        if contactExists:
            xchat.command("query " + word_eol[1])

    return xchat.EAT_ALL


# stub method for now
def check_for_contact(self, contact):
    # search for the contacts in the contacts retrieved from mysms
    # cache the contacts? or pull on startup and then pass around the JSON array?

    # return true if the contact exists or if we specify a phone number
    return False


def message_cb(word, word_eol, userdata):
    # figure out how to replace the string so that we do not send data to the server
    # sending messages to the irc server just yields a "no such nick" response
    print word_eol
    return xchat.EAT_ALL


def receive_response(self):
    # take advantage of the recv command and use it to simulate server response
    xchat.command('recv :Spartacus!~italy@i.am.spartacus PRIVMSG #silarus :No I am Spartacus!')


def add_hooks():
    ''' hook into the text handling of xchat'''
    xchat.hook_print("Channel Message",  message_cb)
    xchat.hook_print("Channel Message Hilight", message_cb)
    xchat.hook_print("Private Message", message_cb)
    xchat.hook_print("Private Message to Dialog", message_cb)
    xchat.hook_print("Message Send", message_cb)
    xchat.hook_print("Your Message", message_cb)
    xchat.hook_print("Channel Action", message_cb)
    xchat.hook_print("Channel Action Hilight", message_cb)

    # xchat.hook_print('Your Message', message_cb)

    # create a hook for the mysms command so that we can initiate messages with a person
    xchat.hook_command("mysms", mysms_cb, help="/mysms <contact> Opens a dialog to a mysms contact.")

# add hooks
add_hooks()
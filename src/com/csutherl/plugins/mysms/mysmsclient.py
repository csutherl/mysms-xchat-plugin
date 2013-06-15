__author__ = 'coty'

import logging
import re

from mysms import MySms
from settings import mysms_config, console


class MySmsClient():
    __MySms = False
    __ContactByName = False
    __ContactByNumber = False

    def __init__(self):
        # setup logging
        self.log = logging.getLogger(name='mysmsclient')
        self.log.setLevel(mysms_config['logging_level'])
        self.log.addHandler(console)

        self.login()
        self.setContacts()

    def login(self):
        # get the API Key from your local settings
        api_key = mysms_config['api_key']
        # initialize class with apiKey and AuthToken(if available)
        self.__MySms = MySms(api_key)

        # lets login user to get AuthToken
        login_data = {'msisdn': mysms_config['accountMsisdn'], 'password': mysms_config['accountPassword']}

        # providing REST type(json/xml), resource from http://api.mysms.com/index.html and POST data
        user_info = self.__MySms.JsonApiCall('/user/login', login_data, False, False)

        if user_info['errorCode'] is not 0:
            # Explanation of codes is here: http://api.mysms.com/resource_User.html#path__user_login.html
            raise Exception('Failed to login. Error code is ' + user_info['errorCode'])

        self.log.debug(user_info)  # debug login data

        self.__MySms.setAuthToken(user_info['authToken'])  # setting up auth Token in class (optional)

    def setContacts(self):
        req_data = {}  # no required data
        contacts = self.__MySms.JsonApiCall('/user/contact/contacts/get', req_data, printRes=False)

        self.log.debug("Contacts loaded. Did not print results to reserve space.")

        # replaced spaces in names with _'s to allow recv to work
        # comprehensions ftw!!
        self.__ContactByName = {re.sub(' ', '_', x['name']): x['msisdns'] for x in contacts['contacts']}
        self.__ContactByNumber = {x['msisdns'][0]: re.sub(' ', '_', x['name']) for x in contacts['contacts']}

    def getContactByName(self):
        return self.__ContactByName

    def getContactNumber(self, contact_name):
        return self.__ContactByName[contact_name][0]

    def getContactName(self, contact_number):
        return self.__ContactByNumber[contact_number]

    def getContactByNumber(self):
        return self.__ContactByNumber

    def verifyContact(self, contact):
        self.log.debug("Verifying contact: %s" % contact)

        # recipients must have '+1' prefix for US numbers
        # if the string does not contain a number, then we try to find its contact
        if re.match('^[+]\d{11}', contact) is None:
            try:
                number = self.__ContactByName[contact][0]
                return number
            except KeyError:
                raise KeyError("Invalid contact.")
        else:
            return contact

    def getLikeContact(self, contact):
        self.log.debug("Get contact like %s" % contact)

        arr = []
        for name in self.__ContactByName:
            if contact.lower() in name.lower():
                # added substring replacement for _ to space to display contacts
                arr.append(re.sub('_', ' ', name))

        return arr

    def sendText(self, contact, message, verifyContact=True):
        # added verify contact so that we can toggle whether or not you want to verify
        if verifyContact:
            contact_phone = self.verifyContact(contact)
        else:
            contact_phone = contact

        req_data = {
            "recipients": [contact_phone],
            "message": message,
            "encoding": 0,
            "smsConnectorId": 0,
            "store": True,
        }

        # calling method ApiCall
        result = self.__MySms.JsonApiCall('/remote/sms/send', req_data)

        return result

    def syncMessages(self, phone_number, number_of_messages):
        req_data = {
            "address": phone_number,
            "offset": 0,
            "limit": number_of_messages,
        }

        # calling method ApiCall
        raw_messages = self.__MySms.JsonApiCall('/user/message/get/by/conversation', req_data, printRes=False)
        messages = {x['messageId']: {'incoming': x['incoming'], 'message': x['message']}
                    for x in raw_messages['messages']}  # comprehension ftw!!

        return messages

if __name__ == "__main__":
    c = MySmsClient()
    # print c.getContactName(mysms_config['test_number'])
    # print c.getLikeContact('shannon')
    # c.sendText(mysms_config['test_number'], 'testing')
    # c.syncMessages(mysms_config['test_number'], 2)

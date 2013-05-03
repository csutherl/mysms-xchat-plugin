from mysms import Mysms
from settings import mysms_config
import json
import logging
from custom_logging import CustomLogging, console


class Client():

    __MySms = False

    def __init__(self):
        # setup logging
        self.log = logging.getLogger(name='client')
        self.log.setLevel(CustomLogging.get_env_specific_logging())
        self.log.addHandler(console)

    def login(self):
        # get the API Key from your local settings
        api_key = mysms_config['api_key']
        # initialize class with apiKey and AuthToken(if available)
        self.__MySms = Mysms(api_key)

        # lets login user to get AuthToken
        login_data = {'msisdn': mysms_config['accountMsisdn'], 'password': mysms_config['accountPassword']}

        login = self.__MySms.ApiCall('json', '/user/login', login_data, False) # providing REST type(json/xml), resource from http://api.mysms.com/index.html and POST data
        self.log.debug(login)
        user_info = json.loads(login)

        if user_info['errorCode'] is not 0:
            raise Exception('Failed to login. Error code is ' + str(user_info['errorCode'])) # Explanation of codes is here: http://api.mysms.com/resource_User.html#path__user_login.html

        self.log.debug(user_info) # debug login data

        self.__MySms.setAuthToken(user_info['authToken']) # setting up auth Token in class (optional)

    def getContacts(self):
        req_data = {} # no required data
        usercontacts = self.__MySms.ApiCall('json', '/user/contact/contacts/get', req_data) # calling method ApiCall
        self.log.debug(usercontacts) # print result

    def sendText(self, number, message):
        # recipients must have '+1' prefix for US numbers
        req_data = {
            "recipients": [number],
            "message": message,
            "encoding": 0,
            "smsConnectorId": 0,
            "store": True,
        }

        sendsms = self.__MySms.ApiCall('json', '/remote/sms/send', req_data) # calling method ApiCall
        self.log.debug(sendsms) # print result

    def sync(self, number):
        req_data = {
            "address": number,
            "offset": 0,
            "limit": 5,
        }

        result = self.__MySms.ApiCall('json', '/user/message/get/by/conversation', req_data) # calling method ApiCall
        self.log.debug(result) # print result

if __name__ == "__main__":
    c = Client()
    c.login()
    # c.getContacts()
    # c.sendText(mysms_config['test_number'], 'testing')
    c.sync(mysms_config['test_number'])

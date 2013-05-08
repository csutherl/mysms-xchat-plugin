from mysms import MySms
from settings import mysms_config
import logging
from custom_logging import CustomLogging, console


class MySmsClient():

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
        self.__MySms = MySms(api_key)

        # lets login user to get AuthToken
        login_data = {'msisdn': mysms_config['accountMsisdn'], 'password': mysms_config['accountPassword']}

        # providing REST type(json/xml), resource from http://api.mysms.com/index.html and POST data
        user_info = self.__MySms.JsonApiCall('/user/login', login_data, False)

        if user_info['errorCode'] is not 0:
            # Explanation of codes is here: http://api.mysms.com/resource_User.html#path__user_login.html
            raise Exception('Failed to login. Error code is ' + str(user_info['errorCode']))

        self.log.debug(user_info) # debug login data

        self.__MySms.setAuthToken(user_info['authToken']) # setting up auth Token in class (optional)

    def getContacts(self):
        req_data = {} # no required data
        self.__MySms.JsonApiCall('/user/contact/contacts/get', req_data) # calling method ApiCall

    def sendText(self, number, message):
        # recipients must have '+1' prefix for US numbers
        req_data = {
            "recipients": [number],
            "message": message,
            "encoding": 0,
            "smsConnectorId": 0,
            "store": True,
        }

        self.__MySms.JsonApiCall('/remote/sms/send', req_data) # calling method ApiCall

    def sync(self, number):
        req_data = {
            "address": number,
            "offset": 0,
            "limit": 5,
        }

        self.__MySms.JsonApiCall('/user/message/get/by/conversation', req_data) # calling method ApiCall

if __name__ == "__main__":
    c = MySmsClient()
    c.login()
    # c.getContacts()
    # c.sendText(mysms_config['test_number'], 'testing')
    c.sync(mysms_config['test_number'])

__author__ = 'coty'

import json
import pycurl
import StringIO
import logging
from custom_logging import CustomLogging, console


class MySms():

    __ApiKey = False
    __AuthToken = False
    __BaseUrl = 'https://api.mysms.com/'

    def __init__(self, apikey, authtoken=False):
        self.__ApiKey = apikey
        self.__AuthToken = authtoken

        # setup logging
        self.log = logging.getLogger(name='mysms')
        self.log.setLevel(CustomLogging.get_env_specific_logging())
        self.log.addHandler(console)

    def setAuthToken(self, authtoken):
        self.__AuthToken = authtoken

    def JsonApiCall(self, resource, data, useAuthToken=True):
        result = self.ApiCall('json', resource, data, useAuthToken)
        return json.loads(result)

    def ApiCall(self, rest, resource, data, useAuthToken=True):
        if rest == '' and rest != 'json' and rest != 'xml':
            raise Exception('Please provide valid REST type: xml/json!') # check if rest is xml or json

        # check if https://api.mysms.com/$rest/$resource is valid url ?

        elif not isinstance(useAuthToken, bool):
            raise Exception('Provided argument is not a boolean value!')

        elif not isinstance(data, (list, tuple, dict)):
            raise Exception('Provide data is not an Array!') # check if provided data is valid array

        else:
            # insert api key into data
            data['apiKey'] = self.__ApiKey

            if useAuthToken:
                # insert authToken key into data
                data['authToken'] = self.__AuthToken

            result = self.curlRequest(rest + resource, data)
            self.log.debug(result)
            return result

    def curlRequest(self, resource, data):
        json_encoded_data = json.dumps(data)

        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, self.__BaseUrl + resource)
        curl.setopt(pycurl.POSTFIELDS, json_encoded_data)
        curl.setopt(pycurl.HTTPHEADER, [                                                                          
            'Content-Type: application/json;charset=utf-8',                                                                           
            'Content-Length: ' + str(len(json_encoded_data))]
        )

        # capture curl output in buffer
        buff = StringIO.StringIO()
        curl.setopt(pycurl.WRITEFUNCTION, buff.write)
        
        curl.perform()
        return buff.getvalue()

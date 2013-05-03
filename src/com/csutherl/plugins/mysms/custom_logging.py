import logging
import os

__author__ = 'smendenh'

# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

TRACE = 5

# create console handler and set level to info
console = logging.StreamHandler()
console.level = logging.DEBUG
console.setFormatter(formatter)


class CustomLogging:
    @staticmethod
    def get_env_specific_logging():
        try:
            if os.environ["ENV"] == "prod":
                console.setLevel(logging.INFO)
                return logging.INFO
        except KeyError as e:
            pass

        console.setLevel(logging.DEBUG)
        return logging.DEBUG
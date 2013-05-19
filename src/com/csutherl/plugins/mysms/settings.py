import logging
import pprint
import os
import yaml
import json

# CustomLogging
# create console handler and set level to info
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# set formatter
console.setFormatter(formatter)
# End CustomLogging

mysms_config = {}

settings_log = logging.getLogger(name="settings")
settings_log.setLevel(logging.DEBUG)
settings_log.addHandler(console)

pp = pprint.PrettyPrinter(indent=4)

settings_filename = '.mysms-settings.yaml'

# Adding this block allows for the config to exist in ~, xchatdir, or cwd
try:
    import xchat
    settings_fs_locs = ["{}/{}".format(xchat.get_info("xchatdir"), settings_filename), "{}/{}".format(os.path.expanduser("~"), settings_filename), "".join(settings_filename)]
except ImportError:
    settings_log.info("Cannot load xchat module.")
    settings_fs_locs = ["{}/{}".format(os.path.expanduser("~"), settings_filename), "".join(settings_filename)]

# TODO: Only grab one file and load it, if that fails try to load the next in the list instead of iterating through the list regardless.
settings_loaded = False
for the_path in settings_fs_locs:
    settings_log.debug("Attempting to load {}".format(the_path))
    try:
        with open(the_path, 'r') as f:
            prop_list = yaml.load(f.read())
            for key, value in prop_list.items():
                mysms_config[key] = value

            settings_log.debug("Settings loaded from %s" % the_path)
            settings_loaded = True
            break
    except (OSError, IOError) as e:
        settings_log.warn("{} {}".format(e.strerror, the_path))


if not settings_loaded:
    settings_log.error("Could not find settings file in {}".format(','.join(settings_fs_locs)))
    exit()

# INFO = 20
# DEBUG = 10
console.level = mysms_config['logging_level']

mysms_config['receive_delay'] = 10 * 1000

## Currently required attributes set in the config are:
#   logging_level: 10
#   api_key: 'YOUR_API_KEY'
#   accountMsisdn: 'YOUR_PHONE_NUMBER'
#   accountPassword: 'YOUR_MYSMS_PASSWORD'


def persist_max_id(self, contact, maxId):
    file_path = "{}/{}/{}/{}".format(xchat.get_info("xchatdir"), "scrollback",
                                     xchat.get_info("network"), "last_msg.json")

    # set data to empty json array
    data = {}

    # try to open file path
    try:
        json_file = open(file_path, "r")
        data = json.load(json_file)
        json_file.close()
    except (OSError, IOError) as e:
        self.log.debug("{} {} {}".format(e.strerror, ". Cannot load ", file_path))

    data[contact] = maxId

    # persist updated json
    try:
        jsonFile = open(file_path, "w+")
        jsonFile.write(json.dumps(data))
        jsonFile.close()
    except (OSError, IOError) as e:
        self.log.debug("{} {} {}".format(e.strerror, ". Cannot load ", file_path))


def get_json_from_file(self):
    file_path = "{}/{}/{}/{}".format(xchat.get_info("xchatdir"), "scrollback",
                                     xchat.get_info("network"), "last_msg.json")
    try:
        json_data = open(file_path)
        data = json.load(json_data)

        self.log.debug(data)

        json_data.close()

        return data
    except IOError:
        self.log.debug("File %s does not exist. Loading all messages." % file_path)
        return None


def get_max_id(self, contact):
    data = get_json_from_file(self)
    self.log.debug("Getting data for contact %s" % contact)

    if data is None:
        return None
    else:
        try:
            return data[contact]
        except KeyError:
            return None

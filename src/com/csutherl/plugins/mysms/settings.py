import logging
import pprint
import os
import yaml

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

## Currently required attributes set in the config are:
#   logging_level: 10
#   api_key: 'YOUR_API_KEY'
#   accountMsisdn: 'YOUR_PHONE_NUMBER'
#   accountPassword: 'YOUR_MYSMS_PASSWORD'


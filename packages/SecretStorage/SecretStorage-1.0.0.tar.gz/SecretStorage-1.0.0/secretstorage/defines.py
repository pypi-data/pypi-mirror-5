# SecretStorage module for Python
# Access passwords using the SecretService DBus API
# Author: Dmitry Shachnev, 2013
# License: BSD

# This file contains some common defines.

SECRETS = 'org.freedesktop.secrets'
SS_PREFIX = 'org.freedesktop.Secret.'
SS_PATH = '/org/freedesktop/secrets'

DBUS_UNKNOWN_METHOD = 'org.freedesktop.DBus.Error.UnknownMethod'
DBUS_SERVICE_UNKNOWN = 'org.freedesktop.DBus.Error.ServiceUnknown'
DBUS_NO_SUCH_OBJECT = 'org.freedesktop.Secret.Error.NoSuchObject'
DBUS_EXEC_FAILED = 'org.freedesktop.DBus.Error.Spawn.ExecFailed'

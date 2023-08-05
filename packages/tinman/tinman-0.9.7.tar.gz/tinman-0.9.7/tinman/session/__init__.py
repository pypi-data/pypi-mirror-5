"""
Session adapters

"""
import logging
import pickle
import os
import tempfile
import time
import uuid

from tinman import exceptions

DEFAULT_DURATION = 300
LOGGER = logging.getLogger(__name__)


class SessionSerializer(object):
    """Base session data serialization object. To use a different session
    serialization format, extend this class and implement the _serialize and
    _deserialize methods.

    """
    def _deserialize(self, data):
        """Return the deserialized session data.

        :param str data: The data to deserialize
        :rtype: dict
        :raises: NotImplementedError

        """
        raise NotImplementedError

    def _serialize(self):
        """Return self._data as a serialized string.

        :rtype: str
        :raises: NotImplementedError

        """
        raise NotImplementedError


class SessionAdapter(object):
    """Base session adapter that facilitates the storage and retrieval of
    session data.

    """
    def __init__(self, application, session_id=None, configuration=None,
                 duration=DEFAULT_DURATION):
        """Create a session adapter for the base URL specified, creating a new
        session if no session id is passed in.

        :param str session_id: The current session id if once has been started
        :param dict configuration: Session storage configuration
        :param int duration: The session duration for storage purposes

        """
        self.__dict__['attributes'] = dict()
        self.__dict__['data'] = dict()
        self._application = application
        self._config = configuration or dict()
        self._duration = duration
        self.__dict__['attributes']['_id'] = session_id or self._create_id()

    def __contains__(self, item):
        """Check to see if the item is in the session data dictionary.

        :param str item: The item to look for

        """
        return item in self.__dict__['data']

    def __delattr__(self, key):
        """Delete a session object's attribute, keeping track of what is
        internal to the object itself and what is a data attribute.

        :param str key: The attribute to remove
        :raises: AttributeError

        """
        if key == '_data':
            self.__dict__['data'] = dict()
        elif key[0] == '_':
            if key in self.__dict__['attributes']:
                del self.__dict__['attributes'][key]
        elif key in self.__dict__['data']:
            del self.__dict__['data'][key]
        else:
            raise AttributeError(key)

    def __getattr__(self, key):
        """Get a session object's attribute, keeping track of what is internal
        to the object and what is a session data attribute.

        :param str key: The key to get the value for
        :rtype: any

        """
        if key == '_data':
            return self.__dict__['data']
        elif key[0] == '_':
            return self.__dict__['attributes'].get(key)
        return self.__dict__['data'].get(key)

    def __hash__(self):
        """Return the hash of the object, using the hash of the session id.

        :rtype: int

        """
        return self.__dict__['attributes']['_id'].hash()

    def __iter__(self):
        """Iterate through the keys in the data dictionary.

        :rtype: list

        """
        return iter(self.__dict__['data'])

    def __len__(self):
        """Return the length of the data dictionary.

        :rtype: int

        """
        return len(self.__dict__['data'])

    def __repr__(self):
        """Return the representation of the class as a string.

        :rtype: str

        """
        return '<%s(%r)>' % (self.__class__.__name__, self.id)

    def __setattr__(self, key, value):
        """Set a session object's attribute, keeping track of what is internal
        to the object and what is a session data attribute.

        :param str key: The attribute name
        :param any value: The value to set

        """
        if key == '_data':
            raise AttributeError('Can not set the _data value')
        if key[0] == '_':
            self.__dict__['attributes'][key] = value
        else:
            self.__dict__['data'][key] = value

    def _create_id(self):
        """Create a session id

        :rtype: str

        """
        return str(uuid.uuid4())

    def _deserialize(self, data):
        """Return the deserialized session data.

        :rtype: str

        """
        return pickle.loads(data)

    def _load_session_data(self):
        """Extend to the load the session from storage

        :raises: NotImplementedError

        """
        raise NotImplementedError

    def _serialize(self):
        """Return the session data as serialized string.

        :rtype: str

        """
        return pickle.dumps(self.__dict__['data'])

    def as_dict(self):
        """Return the SessionAdapter object as a dictionary value, returning
        only the session data attributes in the dictionary.

        :rtype: dict

        """
        return self.__dict__['data']

    def clear(self):
        """Clear all of the attributes in the session."""
        self._data = dict()

    def delete(self):
        """Extend to the delete the session from storage

        :raises: NotImplementedError

        """
        raise NotImplementedError

    def get(self, item, default):
        """Get an item from the session data returning a default value if it
        is not present.

        :param str item: The item in the session data to get
        :param any default: The default value
        :rtype: any

        """
        return self.__dict__['data'].get(item, default)

    @property
    def id(self):
        """A read-only view of the session id.

        """
        return self.__dict__['attributes']['_id']

    def items(self):
        """Return the session data items as a list of key/value tuples.

        :rtype: list

        """
        return self.__dict__['data'].items()

    def keys(self):
        """Return the session data keys

        :rtype: list

        """
        return self.__dict__['data'].keys()

    def load(self):
        """Load the session data"""
        self.__dict__['data'] = self._load_session_data()

    def save(self):
        """Save the session for later retrieval

        :raises: NotImplementedError

        """
        raise NotImplementedError

    def values(self):
        """Return the session data values

        :rtype: list

        """
        return self.__dict__['data'].values()


class FileSessionAdapter(SessionAdapter):
    """Stores session data on the filesystem. Configuration values that can
    be set:

    directory: The directory to store the files in
    cleanup: Boolean value to clean stale session files

    If directory is not set, a directory named "tinman" will be created in the
    default system temp directory for the active user and files will be placed
    in there.

    Cleanup is turned on by default

    """
    SUBDIR = 'tinman'

    def __init__(self, application, session_id=None, configuration=None,
                 duration=DEFAULT_DURATION):
        """Create a session adapter for the base URL specified, creating a new
        session if no session id is passed in.

        :param tinman.application.Application application: The Tinman app
        :param str session_id: The current session id if once has been started
        :param dict configuration: Session storage configuration
        :param int duration: The session duration for storage retention

        """
        super(FileSessionAdapter, self).__init__(application, session_id,
                                                 configuration, duration)
        self._storage_dir = self._setup_storage_dir()
        if self.config.get('cleanup', True):
            self._cleanup()

    def _cleanup(self):
        """Remove any stale files from the session storage directory"""
        for filename in os.listdir(self._storage_dir):
            file_path = '%s/%s' % (self._storage_dir, filename)
            file_stat = os.stat(file_path)
            evaluate = max(file_stat.st_ctime, file_stat.st_mtime)
            if evaluate + self._duration < time.time():
                LOGGER.debug('Removing stale file: %s', file_path)
                os.unlink(file_path)

    @property
    def _default_path(self):
        """Return the default path for session data

        :rtype: str

        """
        return  '%s/%s' % (tempfile.gettempdir(), self.SUBDIR)

    @property
    def _filename(self):
        """Returns the filename for the session file.

        :rtype: str

        """
        return '%s/%s' % (self._storage_dir, self.id)

    def _load_session_data(self):
        """Extend to the load the session from storage

        :rtype: dict
        :raises: IOError

        """
        try:
            with open(self._filename, 'rb') as session_file:
                return self._deserialize(session_file.read()) or dict()
        except IOError as error:
            LOGGER.debug('Session file error: %s', error)
        return dict()

    def _make_path(self, path):
        """Create the full path specified.

        :param str path

        """
        os.makedirs(path, 0755)

    def _setup_storage_dir(self):
        """Setup the storage directory path value and ensure the path exists.

        :rtype: str
        :raises: tinman.exceptions.ConfigurationException

        """
        path = self.config.get('directory')
        if path:
            if not os.path.exists(path) or not os.path.isdir(path):
                raise exceptions.ConfigurationException('FileSessionAdapter '
                                                        'directory')
        else:
            path = self._default_path
            if not os.path.exists(path):
                self._make_path(path)
        return path.rstrip('/')

    def delete(self):
        """Remove the session data from storage, clearing any session values"""
        self.clear()
        if os.path.isfile(self._filename):
            os.unlink(self._filename)
        else:
            LOGGER.debug('Session file did not exist: %s', self._filename)

    def save(self):
        """Store the session for later retrieval

        :raises: IOError

        """
        try:
            with open(self._filename, 'wb') as session_file:
                session_file.write(self._serialize())
        except IOError as error:
            LOGGER.debug('Session file error: %s', error)
            raise error


def get_session_adapter(application, session_id, configuration, duration):

    LOGGER.debug('Returning a new session adapter: %r %r', configuration, duration)

    if configuration.get('class') == 'FileSessionHandler':
        return FileSessionAdapter(application, session_id,
                                  configuration, duration)

    elif configuration.get('class') == 'RedisSessionHandler':
        from tinman.session import redis_adapter
        return redis_adapter.RedisSessionAdapter(application, session_id,
                                                 configuration, duration)

    raise exceptions.ConfigurationException('Session Adapter')

"""A module for connecting to a NuoDB database.

Exported Classes:
Connection -- Class for establishing connection with host.

Exported Functions:
connect -- Creates a connection object.
"""

__all__ = [ 'apilevel', 'threadsafety', 'paramstyle', 'connect', 'Connection' ]

from cursor import Cursor
from encodedsession import EncodedSession
from crypt import ClientPassword, RC4Cipher
from util import getCloudEntry
from session import SessionException
from exception import ProgrammingError

import time
import string
import protocol

# http://www.python.org/dev/peps/pep-0249

apilevel = "2.0"
threadsafety = 1
paramstyle = "qmark"
#schema='user', auto_commit=False
def connect(database, host, user, password, options = None ):
    """Creates a connection object.
    Arguments:
    database -- Name of the database to access.
    host -- NuoDB Broker host. This can include a port (e.g. "localhost:48005")
    user -- The database user
    password -- The database user's password
    options -- A dictionary of NuoDB connection options
        Some common options include:
        "schema"
        
    """
    return Connection(database, host, user, password, options)

class Connection(object):
    
    """Class for establishing a connection with host.
    
    Public Functions:
    testConnection -- Tests to ensure the connection was properly established.
    close -- Closes the connection with the host.
    commit -- Sends a message to the host to commit transaction.
    rollback -- Sends a message to the host to rollback uncommitted changes.
    cursor -- Return a new Cursor object using the connection.
    
    Private Functions:
    __init__ -- Constructor for the Connection class.
    _check_closed -- Checks if the connection to the host is closed.
    
    Special Function:
    auto_commit (getter) -- Gets the value of auto_commit from the database.
    auto_commit (setter) -- Sets the value of auto_commit on the database.
    """
    
    from exception import Warning, Error, InterfaceError, DatabaseError, DataError, \
            OperationalError, IntegrityError, InternalError, \
            ProgrammingError, NotSupportedError
    
    def __init__(self, dbName, broker, username, password, options):
        """Constructor for the Connection class.
        
        Arguments:
        dbName -- Name of database you are accessing.
        broker -- Address of the broker you are connecting too.
        username -- NuoDB username.
        password -- NuoDB password.
        options -- A dictionary of NuoDB connection options
            Some common options include:
            "schema"
        
        Returns:
        a Connection instance
        """
        (host, port) = getCloudEntry(broker, dbName)
        self.__session = EncodedSession(host, port)
        self._trans_id = None

        cp = ClientPassword()
        
        parameters = {'user' : username, 'timezone' : time.strftime('%Z')}
        if options:
            parameters.update(options)

        self.__session.putMessageId(protocol.OPENDATABASE).putInt(protocol.EXECUTEPREPAREDUPDATE).putString(dbName).putInt(len(parameters))
        for (k, v) in parameters.iteritems():
            self.__session.putString(k).putString(v)
        self.__session.putNull().putString(cp.genClientKey())

        self.__session.exchangeMessages()

        version = self.__session.getInt()
        serverKey = self.__session.getString()
        salt = self.__session.getString()

        sessionKey = cp.computeSessionKey(string.upper(username), password, salt, serverKey)
        self.__session.setCiphers(RC4Cipher(sessionKey), RC4Cipher(sessionKey))

        # check auth
        try:
            self.__session.putMessageId(protocol.AUTHENTICATION).putString('Success!')
            self.__session.exchangeMessages()
        except SessionException:
            raise ProgrammingError('Invalid database username or password')
            
        
        # set auto commit to false by default
        self.__session.putMessageId(protocol.SETAUTOCOMMIT).putInt(0)
        
        self.__session.exchangeMessages(False)

    def testConnection(self):
        """Tests to ensure the connection was properly established.
        
        This function will test the connection and if it was created should print out:
        count: 1
        name: ONE
        value: 1
        
        Arguments:
        None
        
        Returns:
        None
        """
        # Create a statement handle
        self.__session.putMessageId(protocol.CREATE)
        self.__session.exchangeMessages()
        handle = self.__session.getInt()

        # Use handle to query dual
        self.__session.putMessageId(protocol.EXECUTEQUERY).putInt(handle).putString('select 1 as one from dual')
        self.__session.exchangeMessages()

        rsHandle = self.__session.getInt()
        count = self.__session.getInt()
        colname = self.__session.getString()
        result = self.__session.getInt()
        fieldValue = self.__session.getInt()
        r2 = self.__session.getInt()

    @property
    def auto_commit(self):
        """Gets the value of auto_commit from the database."""
        self._check_closed()
        self.__session.putMessageId(protocol.GETAUTOCOMMIT)
        self.__session.exchangeMessages()
        return self.__session.getValue()
    
    @auto_commit.setter
    def auto_commit(self, value):
        """Sets the value of auto_commit on the database."""
        self._check_closed()
        self.__session.putMessageId(protocol.SETAUTOCOMMIT).putInt(value)
        self.__session.exchangeMessages(False)

    def close(self):
        """Closes the connection with the host."""
        self._check_closed()
        self.__session.putMessageId(protocol.CLOSE)
        self.__session.exchangeMessages()
        self.__session.closed = True

    def _check_closed(self):
        """Checks if the connection to the host is closed."""
        if self.__session.closed:
            raise self.Error("connection is closed")

    def commit(self):
        """Sends a message to the host to commit transaction."""
        self._check_closed()
        self.__session.putMessageId(protocol.COMMITTRANSACTION)
        self.__session.exchangeMessages()
        self._trans_id = self.__session.getValue()

    def rollback(self):
        """Sends a message to the host to rollback uncommitted changes."""
        self._check_closed()
        self.__session.putMessageId(protocol.ROLLBACKTRANSACTION)
        self.__session.exchangeMessages()

    def cursor(self):
        """Return a new Cursor object using the connection."""
        self._check_closed()
        return Cursor(self.__session)
    

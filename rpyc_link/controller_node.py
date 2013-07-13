import threading
import sys

import rpyc
import rpyc.utils.classic
import rpyc.utils.server

DEFAULT_CONTROLLER_SERVER_PORT = rpyc.utils.classic.DEFAULT_SERVER_PORT + 1

registered_pymol = None
registered_connection = None
_registered_service_id = None

_current_controller_server = None

class PymolControllerService(rpyc.SlaveService):
    def exposed_register_pymol(self, pymol):
        global registered_pymol
        global registered_connection
        global _registered_service_id

        if registered_pymol is not None:
            raise ValueError("Pymol instance already registered.")

        registered_pymol = pymol
        registered_connection = self._conn
        _registered_service_id = id(self)

    def exposed_release_pymol_namespace(self):
        global registered_pymol
        global registered_connection
        global _registered_service_id

        if _registered_service_id is not id(self):
            raise ValueError("Pymol instance not registered.")
        
        registered_pymol = None
        registered_connection = None
        _registered_service_id = None

    def on_disconnect(self):
        global registered_pymol
        global registered_connection
        global _registered_service_id

        if _registered_service_id is id(self):
            registered_pymol = None
            registered_connection = None
            _registered_service_id = None

def start_controller_service(*args, **kwargs):
    """Starts rpyc server hosting PymolControllerService.  *args and *kwargs passed to server.
    
    rpyc server parameters:
    """ + rpyc.utils.server.Server.__doc__

    global _current_controller_server
    if _current_controller_server is not None:
        raise ValueError("Server is already running, close with close_controller_server.")

    #Type conversion, all command line params from pymol are strings
    if not "port" in kwargs:
        kwargs["port"] = DEFAULT_CONTROLLER_SERVER_PORT

    server = rpyc.utils.server.ThreadedServer(PymolControllerService, *args, **kwargs)
    _current_controller_server = server

    thread = threading.Thread(target=server.start, name="pymol_controller_server")
    thread.daemon = True
    thread.start()

def close_controller_server():
    """Closes running controller server."""

    global _current_controller_server
    if _current_controller_server is None:
        raise ValueError("Server is not running.")

    _current_controller_server.close()
    _current_controller_server = None

def connect_rpyc_pymol(host):
    connection = rpyc.utils.classic.connect(host)

    return connection, connection.modules["pymol"]

import pymol

import rpyc
import rpyc.utils.server
import rpyc.utils.classic
import threading

import logging
logger = logging.getLogger("rpyc_link.pymol_node")

from .controller_node import DEFAULT_CONTROLLER_SERVER_PORT

_current_rpyc_server = None

def start_rpyc_server(_self = None, *args, **kwargs):
    """Starts rpyc server hosting rpyc.SlaveService.  *args and *kwargs passed to server.
    
    rpyc server parameters:
    """ + rpyc.utils.server.Server.__doc__

    global _current_rpyc_server
    if _current_rpyc_server is not None:
        raise ValueError("Server is already running, close with close_rpyc_server.")

    #Type conversion, all command line params from pymol are strings
    if "port" in kwargs:
        kwargs["port"] = int(kwargs["port"])
    else:
        kwargs["port"] = rpyc.utils.classic.DEFAULT_SERVER_PORT

    server = rpyc.utils.server.ThreadedServer(rpyc.SlaveService, *args, **kwargs)
    _current_rpyc_server = server

    thread = threading.Thread(target=server.start, name="pymol_rpyc_server")
    thread.daemon = True
    thread.start()

def close_rpyc_server():
    """Closes running rpyc server."""

    global _current_rpyc_server
    if _current_rpyc_server is None:
        raise ValueError("Server is not running.")

    _current_rpyc_server.close()
    _current_rpyc_server = None

def connect_rpyc_controller(host, port=DEFAULT_CONTROLLER_SERVER_PORT):
    import pymol

    conn = rpyc.connect(host, port, service=rpyc.SlaveService)

    bg_service_thread = rpyc.BgServingThread(conn)
    
    conn.root.register_pymol_namespace(pymol)

pymol.cmd.extend('start_rpyc_server', start_rpyc_server)
pymol.cmd.extend('close_rpyc_server', close_rpyc_server)
pymol.cmd.extend('connect_rpyc_controller', connect_rpyc_controller)

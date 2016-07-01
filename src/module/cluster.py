from config import *
import logging
import os
import socket
import subprocess
import pwd
import grp
from bson.dbref import DBRef
from luna.base import Base

class Cluster(Base):
    """
    Class for storing options and procedures for luna
    TODO rename to 'Cluster'
    """

    logging.basicConfig(level=logging.INFO)
#    logging.basicConfig(level=logging.DEBUG)
    _logger = logging.getLogger(__name__)
    _collection_name = None
    _mongo_collection = None
    _keylist = None
    _id = None
    _name = None
    _DBRef = None
    _json = None

    def __init__(self, mongo_db = None, create = False, id = None, nodeprefix = 'node', nodedigits = 3, path = None, user = None, group = None):
        """
        Constructor can be used for creating object by setting create=True
        nodeprefix='node' and nodedigits='3' will give names like node001,
        nodeprefix='compute' and nodedigits='4' will give names like compute0001
        """
        self._logger.debug("Arguments to function '{}".format(self._debug_function()))
        self._logger.debug("Connecting to MongoDB.")
        self._collection_name = 'cluster'
        name = 'general'
        self._mongo_db = mongo_db
        mongo_doc = self._check_name(name, mongo_db, create, id)
        if create:
            try:
                path =  os.path.abspath(path)
            except:
                self._logger.error("No path specified.")
                raise RuntimeError
            if not os.path.exists(path):
                self._logger.error("Wrong path '{}' specified.".format(path))
                raise RuntimeError
            try:
                user_id = pwd.getpwnam(user)
            except:
                self._logger.error("No such user '{}' exists.".format(user))
                raise RuntimeError
            try:
                group_id = grp.getgrnam(group)
            except:
                self._logger.error("No such group '{}' exists.".format(group))
                raise RuntimeError
            path_stat = os.stat(path)
            if path_stat.st_uid != user_id.pw_uid or path_stat.st_gid != group_id.gr_gid:
                self._logger.error("Path is not owned by '{}:{}'".format(user, group))
                raise RuntimeError
            mongo_doc = {'name': name, 'nodeprefix': nodeprefix, 'nodedigits': nodedigits, 'user': user,
                        'debug': 0, 'path': path, 'frontend_address': '', 'frontend_port': '7050',
                        'server_port': 7051, 'tracker_interval': 10,
                        'tracker_min_interval': 5, 'tracker_maxpeers': 200,
                        'torrent_listen_port_min': 7052, 'torrent_listen_port_max': 7200, 'torrent_pidfile': '/run/luna/torrent.pid',
                        'lweb_pidfile': '/run/luna/lweb.pid', 'lweb_num_proc': 0}
            self._logger.debug("mongo_doc: '{}'".format(mongo_doc))
            self._name = name
            self._id = self._mongo_collection.insert(mongo_doc)
            self._DBRef = DBRef(self._collection_name, self._id)
        else:
            self._name = mongo_doc['name']
            self._id = mongo_doc['_id']
            self._DBRef = DBRef(self._collection_name, self._id)
        self._keylist = {'nodeprefix': type(''), 'nodedigits': type(0), 'debug': type(0), 'user': type(''),
                        'path': type(''), 'frontend_address': type(''), 'frontend_port': type(0),
                        'server_port': type(0), 'tracker_interval': type(0),
                        'tracker_min_interval': type(0), 'tracker_maxpeers': type(0),
                        'torrent_listen_port_min': type(0), 'torrent_listen_port_max': type(0), 'torrent_pidfile': type(''),
                        'lweb_pidfile': type(''), 'lweb_num_proc': type(0),
                        'cluster_ips': type('')}

        self._logger.debug("Current instance:'{}".format(self._debug_instance()))

    def __getattr__(self, key):
        try:
            self._keylist[key]
        except:
            raise AttributeError()
        return self.get(key)

    def __setattr__(self, key, value):
        try:
            self._keylist[key]
            self.set(key, value)
        except:
            self.__dict__[key] = value

    def set(self, key, value):
        if key == 'path':
            try:
                value =  os.path.abspath(value)
            except:
                self._logger.error("No path specified.")
                return None
            if not os.path.exists(value):
                self._logger.error("Wrong path specified.")
                return None
            return super(Cluster, self).set(key, value)
        if key in ['server_address', 'tracker_address']:
            try:
                socket.inet_aton(value)
            except:
                self._logger.error("Wrong ip address specified.")
                return None
            return super(Cluster, self).set(key, value)
        if key == 'user':
            try:
                pwd.getpwnam(value)
            except:
                self._logger.error("No such user exists.")
                return None
        if key == 'cluster_ips':
            val = ''
            for ip in value.split(","):
                try:
                    socket.inet_aton(ip.strip())
                except:
                    self._logger.error("Wrong ip address specified.")
                    return None
                val += ip + ','
            val = val[:-1]
            ips = val.split(',')
            return super(Cluster, self).set(key, val)
        return super(Cluster, self).set(key, value)

    def get_cluster_ips(self):
        ips = self.get('cluster_ips')
        ips = ips.split(",")
        local_ip = ''
        for ip in ips:
            stdout = subprocess.Popen(['/usr/sbin/ip', 'addr', 'show', 'to', ip], stdout=subprocess.PIPE).stdout.read()
            if not stdout == '':
                local_ip = ip
                break
        cluster_ips = []
        cluster_ips.append(local_ip)
        for ip in ips:
            if not ip == local_ip:
                cluster_ips.append(ip)
        return cluster_ips

    def is_active(self):
        
        try:
            cluster_ips = self.get('cluster_ips')
        except:
            return True

        ip = self.get('frontend_address')
        if not ip:
            return True
        stdout = subprocess.Popen(['/usr/sbin/ip', 'addr', 'show', 'to', ip], stdout=subprocess.PIPE).stdout.read()
        if stdout:
            return True
        return False
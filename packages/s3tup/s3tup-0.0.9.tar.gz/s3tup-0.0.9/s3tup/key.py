import logging
import mimetypes
import os

import s3tup.utils as utils
import s3tup.constants as constants

log = logging.getLogger('s3tup.key')

class KeyFactory(object):
    """
    Basically just a container for KeyConfigurators. make_key will create a
    key based on the input parameters and then run each configurator on it
    sequentially, returning a fully configured key ready for sync.

    """
    def __init__(self, configurators=None):
        self.configurators = configurators or []

    def make_key(self, conn, key_name, bucket_name):
        """Return a properly configured key"""
        key = Key(conn, key_name, bucket_name)
        return self.configure_key(key)

    def configure_key(self, key):
        for c in self.configurators:
            if c.effects_key(key.name):
                key = c.configure_key(key)
        return key


class KeyConfigurator(object):
    def __init__(self, matcher=None, **kwargs):
        self.matcher = matcher
        for k, v in kwargs.iteritems():
            if k in constants.KEY_ATTRS:
                self.__dict__[k] = v
            else:
                raise TypeError("__init__() got an unexpected keyword"
                                " argument '{}'".format(k))

    def effects_key(self, key_name):
        """Return whether this configurator effects key_name"""
        if self.matcher is None:
            return True
        else:
            return self.matcher.matches(key_name)

    def configure_key(self, key):
        """Return the input key with all configurations applied"""
        for attr in constants.KEY_ATTRS:
            if attr in self.__dict__ and attr != 'metadata':
                key.__dict__[attr] = self.__dict__[attr]

        try: key.metadata.update(self.metadata)
        except AttributeError: pass

        return key


class Key(object):
    """
    Encapsulates configuration for a particular s3 key. It has attributes
    (all defined in constants.KEY_ATTRS) that you can set, delete, modify, 
    and then sync to s3 using the sync or rsync methods.

    """
    def __init__(self, conn, name, bucket_name, **kwargs):
        self.conn = conn
        self.name = name
        self.bucket_name = bucket_name

        # Set defaults for required attributes
        self.reduced_redundancy = kwargs.pop('reduced_redundancy', False)
        self.encrypted = kwargs.pop('encrypted', False)
        self.metadata = kwargs.pop('metadata', {})

        for k,v in kwargs.iteritems():
            if k in constants.KEY_ATTRS:
                self.__dict__[k] = v
            else:
                raise TypeError("__init__() got an unexpected keyword"
                                " argument '{}'".format(k))

    def make_request(self, method, params=None, data=None, headers=None):
        """
        Convenience method for self.conn.make_request; has bucket and key
        already filled in.
        """
        return self.conn.make_request(method, self.bucket_name, self.name,
                                      params, data=data, headers=headers)

    @property
    def headers(self):
        """Return the headers associated with this key"""
        headers = {}

        try: headers['x-amz-acl'] = self.canned_acl
        except AttributeError: pass

        if self.reduced_redundancy:
            headers['x-amz-storage-class'] = 'REDUCED_REDUNDANCY'

        if self.encrypted:
            headers['x-amz-server-side-encryption'] = 'AES256'

        for k, v in self.metadata.iteritems():
            headers['x-amz-meta-' + k] = v

        for k in constants.KEY_HEADERS:
            try:
                if self.__dict__[k] is not None:
                    headers[k.replace('_', '-')] = self.__dict__[k]
            except KeyError: pass

        # Guess content-type
        if 'content-type' not in headers:
            content_type_guess = mimetypes.guess_type(self.name)[0]
            if content_type_guess is not None:
                headers['Content-Type'] = content_type_guess

        return headers

    def sync(self):
        """Sync this object's configuration with its respective key on s3"""
        log.info("syncing key '{}'...".format(self.name))

        headers = self.headers
        headers['x-amz-copy-source'] = '/'+self.bucket_name+'/'+self.name
        headers['x-amz-metadata-directive'] = 'REPLACE'

        self.make_request('PUT', headers=headers)
        self.sync_acl()

    def rsync(self, file_like_object):
        """Upload file_like_object to s3 with this object's configuration"""
        log.info("uploading key '{}'...".format(self.name))

        headers = self.headers
        data = file_like_object.read()

        self.make_request('PUT', headers=headers, data=data)
        self.sync_acl()

    def sync_acl(self):
        try: acl = self.acl
        except AttributeError: return False

        if acl is not None:
            self.make_request('PUT', 'acl', data=acl)
        else:
            self.make_request('PUT', 'acl', headers={'x-amz-acl': 'private'})
        
        
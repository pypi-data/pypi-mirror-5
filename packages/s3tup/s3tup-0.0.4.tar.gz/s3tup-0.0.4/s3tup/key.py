import logging
import mimetypes
import os

import utils
import constants

log = logging.getLogger('s3tup.key')

class KeyFactory(object):

    def __init__(self, conn, bucket_name, configs=[]):
        self.conn = conn
        self.bucket_name = bucket_name

        self.configurators = []
        for c in configs:
            self.configurators.append(self.make_key_configurator(c))

    def make_key_configurator(self, config):
        matcher = utils.Matcher(
            config.pop('patterns', None),
            config.pop('ignore_patterns', None),
            config.pop('regexes', None),
            config.pop('ignore_regexes', None),
        )
        return KeyConfigurator(matcher=matcher, **config)

    def make_key(self, key_name):
        key = Key(self.conn, key_name, self.bucket_name)
        for c in self.configurators:
            if c.effects_key(key.name):
                key = c.configure(key)
        return key


class KeyConfigurator(object):

    def __init__(self, matcher=None, **kwargs):
        self.matcher = matcher

        for k, v in kwargs.iteritems():
            if k in constants.KEY_ATTRS:
                self.__dict__[k] = v
            else:
                raise TypeError("KeyConfigurator.__init__() got an"
                                " unexpected keyword argument'{}'"
                                 .format(attr))

    def effects_key(self, key_name):
        try: return self.matcher.match(key_name)
        except AttributeError: return True

    def configure(self, key):
        for attr in constants.KEY_ATTRS:
            if attr in self.__dict__ and attr != 'metadata':
                key.__dict__[attr] = self.__dict__[attr]

        try: key.metadata.update(self.metadata)
        except AttributeError: pass

        return key


class Key(object):
    
    def __init__(self, conn, name, bucket_name, **kwargs):
        self.conn = conn
        self.name = name
        self.bucket = bucket_name

        # Set defaults for required attributes
        self.reduced_redundancy = kwargs.pop('reduced_redundancy', False)
        self.encrypt = kwargs.pop('encrypt', False)
        self.metadata = kwargs.pop('metadata', {})

        for k,v in kwargs.iteritems():
            if k in constants.KEY_ATTRS:
                self.__dict__[k] = v
            else:
                raise TypeError("Key.__init__() got an unexpected keyword"
                                " argument '{}'".format(attr))

    @property
    def headers(self):
        headers = {}

        try: headers['x-amz-acl'] = self.canned_acl
        except AttributeError: pass

        try:
            if self.reduced_redundancy:
                headers['x-amz-storage-class'] = 'REDUCED_REDUNDANCY'
        except AttributeError: pass

        try: 
            if self.encrypt:
                headers['x-amz-server-side-encryption'] = 'AES256'
        except AttributeError: pass

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
        log.info("syncing key '{}'...".format(self.name))

        headers = self.headers
        headers['x-amz-copy-source'] = '/' + self.bucket + '/' + self.name
        headers['x-amz-metadata-directive'] = 'REPLACE'

        self.conn.make_request('PUT', self.bucket, self.name,
                               headers=headers)
        self.sync_acl()

    def rsync(self, file_like_object):
        log.info("uploading key '{}'...".format(self.name))

        headers = self.headers
        data = file_like_object.read()

        self.conn.make_request('PUT', self.bucket, self.name,
                               headers=headers, data=data)
        self.sync_acl()

    def sync_acl(self):
        try: acl = self.acl
        except AttributeError: return False

        if acl is not None:
            self.conn.make_request('PUT', self.bucket, self.name, 'acl',
                                   data=acl)
        else:
            self.conn.make_request('PUT', self.bucket, self.name, 'acl',
                                   headers={'x-amz-acl': 'private'})
        
        
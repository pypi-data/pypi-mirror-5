#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.concurrent import return_future

from motorengine import ASCENDING
from motorengine.connection import get_connection


class QuerySet(object):
    def __init__(self, klass):
        self.__klass__ = klass
        self._filters = {}
        self._limit = 300
        self._order_fields = []

    @property
    def is_lazy(self):
        return self.__klass__.__lazy__

    def coll(self, alias):
        if alias is not None:
            conn = get_connection(alias=alias)
        else:
            conn = get_connection()

        return conn[self.__klass__.__collection__]

    @return_future
    def create(self, callback, alias=None, **kwargs):
        '''
        Creates and saved a new instance of the document.

        .. testsetup:: saving_create

            import tornado.ioloop
            from motorengine import *

            class User(Document):
                __collection__ = "UserCreatingInstances"
                name = StringField()

            io_loop = tornado.ioloop.IOLoop.instance()
            connect("test", host="localhost", port=4445, io_loop=io_loop)

        .. testcode:: saving_create

            def handle_user_created(user):
                try:
                    assert user.name == "Bernardo"
                finally:
                    io_loop.stop()

            def create_user():
                User.objects.create(name="Bernardo", callback=handle_user_created)

            io_loop.add_timeout(1, create_user)
            io_loop.start()
        '''
        document = self.__klass__(**kwargs)
        self.save(document=document, callback=callback, alias=alias)

    def handle_save(self, document, callback):
        def handle(*arguments, **kw):
            if len(arguments) > 1 and arguments[1]:
                raise arguments[1]

            document._id = arguments[0]
            callback(document)

        return handle

    def handle_update(self, document, callback):
        def handle(*arguments, **kw):
            if len(arguments) > 1 and arguments[1]:
                raise arguments[1]

            callback(document)

        return handle

    def save(self, document, callback, alias=None):
        if not isinstance(document, self.__klass__):
            raise ValueError("This queryset for class '%s' can't save an instance of type '%s'." % (
                self.__klass__.__name__,
                document.__class__.__name__,
            ))

        if document.validate():
            doc = document.to_son()
            if document._id is not None:
                self.coll(alias).update({'_id': document._id}, doc, callback=self.handle_update(document, callback))
            else:
                self.coll(alias).insert(doc, callback=self.handle_save(document, callback))

    @return_future
    def delete(self, callback=None, alias=None):
        '''
        Removes all instance of this document that match the specified filters (if any).

        .. testsetup:: saving_delete

            import tornado.ioloop
            from motorengine import *

            class User(Document):
                __collection__ = "UserDeletingInstances"
                name = StringField()

            io_loop = tornado.ioloop.IOLoop.instance()
            connect("test", host="localhost", port=4445, io_loop=io_loop)

        .. testcode:: saving_delete

            def handle_user_created(user):
                User.objects.filter(name="Bernardo").delete(callback=handle_users_deleted)

            def handle_users_deleted(number_of_deleted_items):
                try:
                    assert number_of_deleted_items == 1
                finally:
                    io_loop.stop()

            def create_user():
                user = User(name="Bernardo")
                user.save(callback=handle_user_created)

            io_loop.add_timeout(1, create_user)
            io_loop.start()
        '''

        self.remove(callback=callback, alias=alias)

    def handle_remove(self, callback):
        def handle(*args, **kw):
            callback(args[0]['n'])

        return handle

    def remove(self, instance=None, callback=None, alias=None):
        if callback is None:
            raise RuntimeError("The callback argument is required")

        if instance is not None:
            if hasattr(instance, '_id') and instance._id:
                self.coll(alias).remove(instance._id, callback=self.handle_remove(callback))
        else:
            if self._filters:
                self.coll(alias).remove(self._filters, callback=self.handle_remove(callback))
            else:
                self.coll(alias).remove(callback=self.handle_remove(callback))

    def handle_auto_load_references(self, doc, callback):
        def handle(*args, **kw):
            if len(args) > 0:
                callback(doc)
                return

            callback(None)

        return handle

    def handle_get(self, callback):
        def handle(*args, **kw):
            instance = args[0]

            if instance is None:
                callback(None)
            else:
                doc = self.__klass__.from_son(instance)
                if self.is_lazy:
                    callback(doc)
                else:
                    doc.load_references(callback=self.handle_auto_load_references(doc, callback))

        return handle

    @return_future
    def get(self, id=None, callback=None, alias=None, **kwargs):
        '''
        Gets a single item of the current queryset collection using it's id.

        In order to query a different database, please specify the `alias` of the database to query.
        '''
        if id is None and not kwargs:
            raise RuntimeError("Either an id or a filter must be provided to get")

        if id is not None:
            filters = {
                "_id": id
            }
        else:
            filters = self.to_filters(**kwargs)

        self.coll(alias).find_one(filters, callback=self.handle_get(callback))

    def to_filters(self, **kwargs):
        filters = {}
        for field_name, value in kwargs.items():
            if field_name not in self.__klass__._fields:
                raise ValueError("Invalid filter '%s': Field not found in '%s'." % (field_name, self.__klass__.__name__))
            field = self.__klass__._fields[field_name]
            filters[field.db_field] = field.to_son(value)

        return filters

    def filter(self, **kwargs):
        '''
        Filters a queryset in order to produce a different set of document from subsequent queries.

        Usage::

            User.objects.filter(first_name="Bernardo").filter(last_name="Bernardo").find_all(callback="handle_all")
            # or
            User.objects.filter(first_name="Bernardo", starting_year__gt=2010).find_all(callback=handle_all)

        The available filter options are the same as used in MongoEngine.
        '''
        filters = self.to_filters(**kwargs)
        self._filters.update(filters)
        return self

    def limit(self, limit):
        '''
        Limits the number of documents to return in subsequent queries.

        Usage::

            User.objects.limit(10).find_all(callback="handle_all")  # even if there are 100s of users,
                                                                    # only first 10 will be returned
        '''

        self._limit = limit
        return self

    def order_by(self, field_name, direction=ASCENDING):
        '''
        Specified the order to be used when returning documents in subsequent queries.

        Usage::

            from motorengine import DESCENDING  # or ASCENDING

            User.objects.order_by('first_name', direction=DESCENDING).find_all(callback="handle_all")
        '''

        if field_name not in self.__klass__._fields:
            raise ValueError("Invalid order by field '%s': Field not found in '%s'." % (field_name, self.__klass__.__name__))

        field = self.__klass__._fields[field_name]
        self._order_fields.append((field.db_field, direction))
        return self

    def handle_find_all(self, callback):
        def handle(*arguments, **kwargs):
            if arguments and len(arguments) > 1 and arguments[1]:
                raise arguments[1]

            result = []
            for doc in arguments[0]:
                result.append(self.__klass__.from_son(doc))

            callback(result)

        return handle

    def _get_find_cursor(self, alias):
        find_arguments = {}

        if self._order_fields:
            find_arguments['sort'] = self._order_fields

        return self.coll(alias).find(self._filters, **find_arguments)

    @return_future
    def find_all(self, callback, alias=None):
        '''
        Returns a list of items in the current queryset collection that match specified filters (if any).

        In order to query a different database, please specify the `alias` of the database to query.

        Usage::

            User.objects.find_all(callback=handle_all_users)

            def handle_all_users(result):
                # do something with result
                # result is None if no users found
                pass
        '''
        to_list_arguments = dict(callback=self.handle_find_all(callback))

        if self._limit is not None:
            to_list_arguments['length'] = self._limit

        self._get_find_cursor(alias=alias).to_list(**to_list_arguments)

    def handle_count(self, callback):
        def handle(*arguments, **kwargs):
            if arguments and len(arguments) > 1 and arguments[1]:
                raise arguments[1]
            callback(arguments[0])

        return handle

    @return_future
    def count(self, callback, alias=None):
        '''
        Returns the number of documents in the collection that match the specified filters (if any).
        '''
        self._get_find_cursor(alias=alias).count(callback=self.handle_count(callback))

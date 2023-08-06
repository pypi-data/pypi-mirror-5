import re
from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
from django.utils import simplejson as json
from django.db.models.fields.files import FileField
from django.db.models.fields.related import ForeignKey
from django.views.decorators.csrf import csrf_exempt

try:
    from django.conf.urls import patterns, include, url
except ImportError:
    from django.conf.urls.defaults import patterns, include, url


class Utils:

    # return `string` underscored e.g.
    # bigData/ big data -> big_data
    def get_underscored_string(self, string):
        return re\
            .sub('(?!^)([A-Z]+)', r'_\1', string)\
            .replace(' ', '_')\
            .lower()


class Permission(Utils):
    def __init__(self, model, attr):
        if not getattr(model, attr, None):
            opts = (model.__name__, attr)
            raise Exception(
                'please implement %s.%s(self, req)' % opts
            )


class Field(Utils):

    def __init__(self, name, field):
        self.name = name
        self.field = field

    @property
    def underscored_name(self):
        return self.get_underscored_string(self.name)

    @property
    def belongs_to_name(self):
        return self.underscored_name + '_id'

    @property
    def model(self):
        return self.field.rel.to


class Relation(Utils):

    def __init__(self, relation):
        self.relation = relation

    @property
    def name(self):
        return self.get_underscored_string(
            self.relation.field.verbose_name
        )

    @property
    def model(self):
        try:
            return self.relation.opts.concrete_model().__class__
        except AttributeError:
            return self.relation.model().__class__

    def get_items(self, item):
        query = {}
        query[self.name] = item
        for obj in self.model.objects.filter(**query):
            yield obj


class Api(Utils):
    def __init__(self, cls):

        self.cls = cls
        self.model = cls.model
        self.fields = cls.fields

        for attr in [
            '__is_creatable__',
            '__is_readable__',
            '__is_updatable__',
            '__is_removable__'
        ]:
            Permission(self.model, attr)

    @property
    def name(self):
        return self.get_underscored_string(self.model.__name__)

    @property
    def plural_name(self):
        plural_name = getattr(self.cls, 'plural_name', None)
        if not plural_name:
            plural_name = self.name + 's'
        return plural_name

    @property
    def field_list(self):
        for field_name in self.fields:
            field = self.model._meta.get_field(field_name)
            yield Field(field_name, field)

    def item_to_JSON(self, item):

        items_string = serializers.serialize('json', [item], fields=self.fields)
        items_json = json.loads(items_string)
        item_json = items_json[0]
        item_data = item_json['fields']
        item_data['id'] = item_json['pk']

        for field in self.field_list:

            if isinstance(field.field, ForeignKey):
                pk = item_data[field.underscored_name]
                del item_data[field.underscored_name]
                item_data[field.belongs_to_name] = pk

            elif isinstance(field.field, FileField):
                file_path = item_data[field.name]
                if file_path:
                    del item_data[field.name]
                    item_data[field.underscored_name] = settings.MEDIA_URL + file_path

        return item_data

    @property
    def relations(self):
        for item in self.model._meta.get_all_related_objects():
            if type(item.field) == ForeignKey:
                yield Relation(item)

    def get_body(self, req):
        try:
            body = req.body
        except AttributeError:
            body = req.raw_post_data
        finally:
            return body

    # update `item` with `req`.body
    def __update__(self, req, item):

        body = self.get_body(req)
        data = json.loads(body)[self.name]

        for field in self.field_list:
            value = None
            if isinstance(field.field, ForeignKey):
                pk = data.get(field.belongs_to_name, None)
                if pk:
                    value = field.model.objects.get(pk=pk)
            else:
                value = data.get(field.underscored_name, None)
            if value:
                setattr(item, field.name, value)

    @property
    def urls(self):
        return [
            url(
                  r'^%s/$' % self.plural_name
                , self.all
                , name=self.plural_name
            ),
            url(
                  r'^%s/(?P<pk>\d+)/$' % self.plural_name
                , self.one
                , name=self.name
            ),
        ]

    # GET /`model`/
    @csrf_exempt
    def all(self, req):

        if req.method == 'POST':

            body = self.get_body(req)
            if json.loads(body).get('query', None):
                return self.query(req)
            return self.create(req)

        def get_items_json():
            items = self.model.objects.all()
            for item in items:
                is_readable = item.__is_readable__(req)
                if not isinstance(is_readable, HttpResponse):
                    yield self.item_to_JSON(item)

        json_data = {}
        json_data[self.plural_name] = [ i for i in get_items_json() ]

        return HttpResponse(
            json.dumps(json_data), content_type='application/json'
        )

    # QUERY /`model`/
    @csrf_exempt
    def query(self, req):

        items = self.model.objects
        body = self.get_body(req)
        query = json.loads(body)['query']

        # filter
        filta = query.get('filter', None)
        if filta:
            items = items.filter(**filta)

        # exclude
        exclude = query.get('exclude', None)
        if exclude:
            items = items.exclude(**exclude)

        # order_by
        order_by = query.get('order_by', '?')
        items = items.order_by(order_by)

        # limit
        limit = query.get('limit', None)
        if limit:
            if len(limit) == 2:
                limit.append(1)
            items = items[limit[0]: limit[1]: limit[2]]

        def get_items_json():
            for item in items:
                is_readable = item.__is_readable__(req)
                if not isinstance(is_readable, HttpResponse):
                    yield self.item_to_JSON(item)

        json_data = {}
        json_data[self.plural_name] = [ i for i in get_items_json() ]

        return HttpResponse(
            json.dumps(json_data), content_type='application/json'
        )

    # METHOD /`model`/`pk`/
    @csrf_exempt
    def one(self, req, pk):
        if req.method == 'PUT':
            return self.update(req, pk)
        elif req.method == 'DELETE':
            return self.remove(req, pk)
        else:
            return self.get(req, pk)

    # POST /`model`/
    def create(self, req):

        item = self.model()
        self.__update__(req, item)

        # note, __is_creatable__ should override any set attributes
        is_creatable = item.__is_creatable__(req)
        if isinstance(is_creatable, HttpResponse):
            res = is_creatable
            return res

        item.save()

        return self.get(req, item.pk)

    # GET /`model`/`pk`/
    def get(self, req, pk):
        item = self.model.objects.get(pk=pk)
        is_readable = item.__is_readable__(req)
        if isinstance(is_readable, HttpResponse):
            res = is_readable
            return res
        json_data = {}
        json_data[self.name] = self.item_to_JSON(item)
        return HttpResponse(
            json.dumps(json_data), content_type='application/json'
        )

    # PUT /`model`/`pk`/
    def update(self, req, pk):

        item = self.model.objects.get(pk=pk)
        self.__update__(req, item)

        is_updatable = item.__is_updatable__(req)
        if isinstance(is_updatable, HttpResponse):
            res = is_updatable
            return res

        item.save()

        return self.get(req, pk)

    # DELETE /`model`/`pk`/
    def remove(self, req, pk):

        item = self.model.objects.get(pk=pk)

        is_removable = item.__is_removable__(req)
        if isinstance(is_removable, HttpResponse):
            res = is_removable
            return res

        item.delete()

        return HttpResponse(json.dumps(''))


class Apis(list):

    def __init__(self, *args):
        super(list, self).__init__()

        for cls in args:
            api = Api(cls)
            for url in api.urls:
                self.append(url)

    @property
    def urls(self):
        return patterns('',
            *self
        )

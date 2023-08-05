import logging
from pyramid.view import view_config

from ringo.views.base import list_, create_, update_, read_, delete_
from ringo.model.modul import ModulItem

log = logging.getLogger(__name__)


@view_config(route_name=ModulItem.get_action_routename('list'),
             renderer='/default/list.mako',
             permission='list')
def list(request):
    return list_(ModulItem, request)


@view_config(route_name=ModulItem.get_action_routename('create'),
             renderer='/default/create.mako',
             permission='create')
def create(request):
    return create_(ModulItem, request)


@view_config(route_name=ModulItem.get_action_routename('update'),
             renderer='/default/update.mako',
             permission='update')
def update(request):
    return update_(ModulItem, request)


@view_config(route_name=ModulItem.get_action_routename('read'),
             renderer='/default/read.mako',
             permission='read')
def read(request):
    return read_(ModulItem, request)


@view_config(route_name=ModulItem.get_action_routename('delete'),
             renderer='/default/confirm.mako',
             permission='delete')
def delete(request):
    return delete_(ModulItem, request)

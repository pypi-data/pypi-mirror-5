from pprint import pprint

from django.test import TestCase

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.routers import ExtendedDefaultRouter
from rest_framework_extensions.decorators import link, action


class TestExtendedDefaultRouterRouter(TestCase):
    def setUp(self):
        self.router = ExtendedDefaultRouter()

    def get_routes_names(self, routes):
        return [i.name for i in routes]

    def get_dynamic_route_by_def_name(self, def_name, routes):
        try:
            return [i for i in routes if def_name in i.mapping.values()][0]
        except IndexError:
            return None

    def test_dynamic_routes_should_be_first_in_order(self):
        class BasicViewSet(viewsets.ViewSet):
            def list(self, request, *args, **kwargs):
                return Response({'method': 'list'})

            @action()
            def action1(self, request, *args, **kwargs):
                return Response({'method': 'action1'})

            @link()
            def link1(self, request, *args, **kwargs):
                return Response({'method': 'link1'})

        routes = self.router.get_routes(BasicViewSet)
        expected = [
            '{basename}-action1',
            '{basename}-link1',
            '{basename}-list',
            '{basename}-detail'
        ]
        msg = '@action and @link methods should come first in routes order'
        self.assertEquals(self.get_routes_names(routes), expected, msg)

    def test_action_endpoint(self):
        class BasicViewSet(viewsets.ViewSet):
            @action(endpoint='action-one')
            def action1(self, request, *args, **kwargs):
                pass

        routes = self.router.get_routes(BasicViewSet)
        action1_route = self.get_dynamic_route_by_def_name('action1', routes)

        msg = '@action with endpoint route should map methods to endpoint if it is specified'
        self.assertEquals(action1_route.mapping, {'post': 'action1'}, msg)

        msg = '@action with endpoint route should use url with detail lookup'
        self.assertEquals(action1_route.url, u'^{prefix}/{lookup}/action-one/$', msg)

    def test_link_endpoint(self):
        class BasicViewSet(viewsets.ViewSet):
            @link(endpoint='link-one')
            def link1(self, request, *args, **kwargs):
                pass

        routes = self.router.get_routes(BasicViewSet)
        link1_route = self.get_dynamic_route_by_def_name('link1', routes)

        msg = '@link with endpoint route should map methods to endpoint if it is specified'
        self.assertEquals(link1_route.mapping, {'get': 'link1'}, msg)

        msg = '@link with endpoint route should use url with detail lookup'
        self.assertEquals(link1_route.url, u'^{prefix}/{lookup}/link-one/$', msg)

    def test_action__for_list(self):
        class BasicViewSet(viewsets.ViewSet):
            @action(is_for_list=True)
            def action1(self, request, *args, **kwargs):
                pass

        routes = self.router.get_routes(BasicViewSet)
        action1_route = self.get_dynamic_route_by_def_name('action1', routes)

        msg = '@action with is_for_list=True route should map methods to def name'
        self.assertEquals(action1_route.mapping, {'post': 'action1'}, msg)

        msg = '@action with is_for_list=True route should use url in list scope'
        self.assertEquals(action1_route.url, u'^{prefix}/action1/$', msg)

    def test_action__for_list__and__with_endpoint(self):
        class BasicViewSet(viewsets.ViewSet):
            @action(is_for_list=True, endpoint='action-one')
            def action1(self, request, *args, **kwargs):
                pass

        routes = self.router.get_routes(BasicViewSet)
        action1_route = self.get_dynamic_route_by_def_name('action1', routes)

        msg = '@action with is_for_list=True and endpoint route should map methods to "endpoint"'
        self.assertEquals(action1_route.mapping, {'post': 'action1'}, msg)

        msg = '@action with is_for_list=True and endpoint route should use url in list scope with "endpoint" value'
        self.assertEquals(action1_route.url, u'^{prefix}/action-one/$', msg)

    def test_actions__for_list_and_detail_with_exact_names(self):
        class BasicViewSet(viewsets.ViewSet):
            @action(is_for_list=True, endpoint='action-one')
            def action1(self, request, *args, **kwargs):
                pass

            @action(endpoint='action-one')
            def action1_detail(self, request, *args, **kwargs):
                pass

        routes = self.router.get_routes(BasicViewSet)
        action1_list_route = self.get_dynamic_route_by_def_name('action1', routes)
        action1_detail_route = self.get_dynamic_route_by_def_name('action1_detail', routes)

        self.assertEquals(action1_list_route.mapping, {'post': 'action1'})
        self.assertEquals(action1_list_route.url, u'^{prefix}/action-one/$')

        self.assertEquals(action1_detail_route.mapping, {'post': 'action1_detail'})
        self.assertEquals(action1_detail_route.url, u'^{prefix}/{lookup}/action-one/$')

    def test_action_names(self):
        class BasicViewSet(viewsets.ViewSet):
            @action(is_for_list=True)
            def action1(self, request, *args, **kwargs):
                pass

            @action()
            def action2(self, request, *args, **kwargs):
                pass

        routes = self.router.get_routes(BasicViewSet)
        action1_list_route = self.get_dynamic_route_by_def_name('action1', routes)
        action2_detail_route = self.get_dynamic_route_by_def_name('action2', routes)

        self.assertEquals(action1_list_route.name, u'{basename}-action1-list')
        self.assertEquals(action2_detail_route.name, u'{basename}-action2')

    def test_action_names__with_endpoints(self):
        class BasicViewSet(viewsets.ViewSet):
            @action(is_for_list=True, endpoint='action_one')
            def action1(self, request, *args, **kwargs):
                pass

            @action(endpoint='action-two')
            def action2(self, request, *args, **kwargs):
                pass

        routes = self.router.get_routes(BasicViewSet)
        action1_list_route = self.get_dynamic_route_by_def_name('action1', routes)
        action2_detail_route = self.get_dynamic_route_by_def_name('action2', routes)

        self.assertEquals(action1_list_route.name, u'{basename}-action-one-list')
        self.assertEquals(action2_detail_route.name, u'{basename}-action-two')
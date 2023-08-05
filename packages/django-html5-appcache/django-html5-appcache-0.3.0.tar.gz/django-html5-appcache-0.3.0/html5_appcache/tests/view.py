# -*- coding: utf-8 -*-
import re

from html5_appcache.cache import reset_cache_manifest
from html5_appcache.models import GlobalPermission
from html5_appcache.test_utils.base import BaseDataTestCase
from html5_appcache.views import ManifestAppCache, CacheStatusView, ManifestUpdateView


class ManifestViewTest(BaseDataTestCase):
    version_rx = re.compile(r"version: \$([0-9\.]+)\$")

    @classmethod
    def setUpClass(cls):
        cls.cache_perm = GlobalPermission.objects.create(codename="can_view_cache_status")
        cls.manifest_perm = GlobalPermission.objects.create(codename="can_update_manifest")
        super(ManifestViewTest, cls).setUpClass()

    def test_manifest_version(self):
        request = self.get_request('/', user=self.admin)
        view = ManifestAppCache.as_view()
        response = view(request, appcache_update=1)
        version = self.version_rx.findall(response.content)
        self.assertTrue(version)
        reset_cache_manifest()
        response = view(request, appcache_update=1)
        version2 = self.version_rx.findall(response.content)
        self.assertNotEqual(version, version2)

    def test_update_manifest_view_noauth(self):
        request = self.get_request('/')
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        view = ManifestUpdateView.as_view()
        response = view(request, appcache_update=1)
        self.assertTrue(response.content.find('"success": false') > -1)

    def test_update_manifest_staff(self):
        self.user.user_permissions.add(self.manifest_perm)
        request = self.get_request('/', user=self.user)
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        view = ManifestUpdateView.as_view()
        response = view(request, appcache_update=1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.find("OK") > -1)
        self.user.user_permissions.remove(self.manifest_perm)

        request = self.get_request('/', user=self.user)
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        view = ManifestUpdateView.as_view()
        response = view(request, appcache_update=1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.find('"success": false') > -1)

    def test_update_manifest_no_ajax(self):
        self.user.user_permissions.add(self.manifest_perm)
        request = self.get_request('/', user=self.user)
        view = ManifestUpdateView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.user.user_permissions.remove(self.manifest_perm)

    def test_cache_status_noauth(self):
        request = self.get_request('/')
        view = CacheStatusView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 403)

    def test_cache_status_staff(self):
        self.user.user_permissions.add(self.cache_perm)
        request = self.get_request('/', user=self.user)
        view = CacheStatusView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.user.user_permissions.remove(self.cache_perm)

        request = self.get_request('/', user=self.user)
        view = CacheStatusView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 403)

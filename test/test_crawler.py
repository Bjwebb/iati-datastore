import datetime
from unittest import TestCase

import mock

from . import AppTestCase

from iatilib import crawler
from iatilib.model import Dataset, Resource


class TestCrawler(AppTestCase):
    @mock.patch('iatilib.crawler.ckanclient.CkanClient.package_register_get')
    def test_fetch_package_list(self, mock):
        mock.return_value = [u"tst-a", u"tst-b"]
        datasets = crawler.fetch_dataset_list()
        self.assertIn("tst-a", [ds.name for ds in datasets])
        self.assertIn("tst-b", [ds.name for ds in datasets])

    @mock.patch('iatilib.crawler.ckanclient.CkanClient.package_register_get')
    def test_fetch_time(self, mock):
        mock.return_value = [u"tst-a"]
        datasets = crawler.fetch_dataset_list()
        self.assertAlmostEqual(
            datetime.datetime.utcnow(),
            datasets[0].first_seen,
            delta=datetime.timedelta(seconds=5))
        self.assertAlmostEqual(
            datetime.datetime.utcnow(),
            datasets[0].last_seen,
            delta=datetime.timedelta(seconds=5))

    @mock.patch('iatilib.crawler.ckanclient.CkanClient.package_register_get')
    def test_update_adds_datasets(self, mock):
        mock.return_value = [u"tst-a"]
        datasets = crawler.fetch_dataset_list()
        mock.return_value = [u"tst-a", u"tst-b"]
        datasets = crawler.fetch_dataset_list()
        self.assertEquals(2, len(datasets))

    @mock.patch('iatilib.crawler.ckanclient.CkanClient.package_entity_get')
    def test_fetch_dataset(self, mock):
        mock.return_value = {"resources": [{"url": "http://foo"}]}
        dataset = crawler.fetch_dataset_metadata(Dataset())
        self.assertEquals(1, len(dataset.resources))
        self.assertEquals("http://foo", dataset.resources[0].url)

    @mock.patch('iatilib.crawler.requests')
    def test_fetch_resource_succ(self, mock):
        mock.get.return_value.text = u"test"
        mock.get.return_value.status_code = 200
        resource = crawler.fetch_resource(Resource(url="http://foo"))
        self.assertEquals(u"test", resource.document)

    @mock.patch('iatilib.crawler.requests')
    def test_fetch_resource_perm_fail(self, mock):
        mock.get.return_value.status_code = 404
        resource = crawler.fetch_resource(Resource(
            url="http://foo",
            document=u"stillhere"
        ))
        self.assertEquals(404, resource.last_status_code)
        self.assertEquals(u"stillhere", resource.document)


class TestDate(TestCase):
    def test_date(self):
        self.assertEquals(
            "Wed, 22 Oct 2008 10:52:40 GMT",
            crawler.http_date(datetime.datetime(2008, 10, 22, 11, 52, 40))
        )

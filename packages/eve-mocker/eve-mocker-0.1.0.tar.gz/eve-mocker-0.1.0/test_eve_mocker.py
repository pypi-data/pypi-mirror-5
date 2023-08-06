# -*- coding: utf-8 -*-

""" test_eve_mocker.py - Test the eve_mocker module. """

import unittest
import requests
from httpretty import HTTPretty
from sure import expect
from eve_mocker import EveMocker, query_data
from urlparse import urljoin
from functools import partial
import json

BASE_URL = "http://localhost/api/"
api_url = partial(urljoin, BASE_URL)


class TestEveMocker(unittest.TestCase):
    def setUp(self):
        HTTPretty.enable()
        self.eve_mocker = EveMocker(BASE_URL, default_pk="testpk")

    def tearDown(self):
        HTTPretty.disable()

    def testAPI(self):
        """ Testing all client features. """
        mymodel_url = api_url("mymodel")
        mymodel1 = {"testpk": "mypk1", "content": "test content"}

        # Check that mymodel resource is empty
        response = requests.get(mymodel_url)
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("_items")
        expect(data["_items"]).to.be.empty

        # Posting mymodel1
        response = requests.post(mymodel_url,
                                 {"mymodel1": json.dumps(mymodel1)})
        data = response.json()

        # Check the status of the item and if it has an etag
        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("mymodel1")
        expect(data["mymodel1"]["status"]).to.equal("OK")
        expect(data["mymodel1"]).to.have.key("etag")

        # Storing the ETag for later
        mymodel1_etag = data["mymodel1"]["etag"]

        # Check that it has actually been created
        response = requests.get(mymodel_url)
        mymodel1_test = mymodel1.copy()
        mymodel1_test.update({"etag": data["mymodel1"]["etag"]})

        expect(response.status_code).to.equal(200)
        expect(response.json()).to.equal({"_items": [mymodel1_test]})

        # Check if we can retrieve the item via its URI
        response = requests.get(api_url("mymodel/mypk1/"))
        data = response.json()

        expect(response.status_code).to.equal(200)

        expect(data).to.equal(mymodel1_test)

        # Check that we CAN'T rePOST mymodel1 with the same primary key
        response = requests.post(mymodel_url,
                                 {"mymodel1": json.dumps(mymodel1)})
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("mymodel1")
        expect(data["mymodel1"]["status"]).to.equal("ERR")

        # Now we try to PATCH the item without If-Match header
        mymodel1_patch = {"content": "new content"}
        response = requests.patch(api_url("mymodel/mypk1/"),
                                  {"data": json.dumps(mymodel1_patch)})

        expect(response.status_code).to.equal(403)

        # Check that it doesn't work with the wrong ETag
        response = requests.patch(api_url("mymodel/mypk1/"),
                                  {"data": json.dumps(mymodel1_patch)},
                                  headers={"If-Match": "falsyetag"})

        expect(response.status_code).to.equal(412)

        # Finally we PATCH with the good ETag
        response = requests.patch(api_url("mymodel/mypk1/"),
                                  {"data": json.dumps(mymodel1_patch)},
                                  headers={"If-Match": mymodel1_etag})
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("data")
        expect(data["data"]["status"]).to.equal("OK")
        expect(data["data"]).to.have.key("etag")

        mymodel1_etag = data["data"]["etag"]
        mymodel1_test.update({"etag": mymodel1_etag,
                              "content": "new content"})

        # Check if the item has been updated
        response = requests.get(api_url("mymodel/mypk1/"))
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.equal(mymodel1_test)

        # Delete without ETag should return 403
        response = requests.delete(api_url("mymodel/mypk1/"))

        expect(response.status_code).to.equal(403)

        # Delete with a WRONG ETag should return 412
        response = requests.delete(api_url("mymodel/mypk1/"),
                                   headers={"If-Match": "wrongetag"})

        expect(response.status_code).to.equal(412)

        # Now we delete it the right way
        response = requests.delete(api_url("mymodel/mypk1/"),
                                   headers={"If-Match": mymodel1_etag})

        expect(response.status_code).to.equal(200)

        # Check that mymodel resource is empty
        response = requests.get(mymodel_url)
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("_items")
        expect(data["_items"]).to.be.empty

    def testSetResource(self):
        """ Test that EveMocker.set_resource works. """
        test_items = sorted([{"testpk": "pk1", "content": "content1"},
                             {"testpk": "pk2", "content": "content2"}])

        self.eve_mocker.set_resource("testresource", test_items)

        # Check that we retireve the items on a GET call
        response = requests.get(api_url("testresource/"))
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("_items")
        expect(sorted(data["_items"])).to.equal(test_items)

    def testFiltering(self):
        """ Test ?where query with basic filtering. """
        test_items = sorted([{"testpk": "pk1", "content": "content1"},
                             {"testpk": "pk2", "content": "content2"}])

        self.eve_mocker.set_resource("testresource", test_items)

        # Check that we retireve the items on a GET call
        response = requests.get(api_url('testresource/?where={"content": "content1"}'))
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("_items")
        expect(sorted(data["_items"])).to.equal([{"testpk": "pk1", "content": "content1"}])

    def testFilteringMongoQuery(self):
        """ Test ?where query with with mongo query syntax filtering. """
        test_items = [{"testpk": i} for i in range(50)]

        self.eve_mocker.set_resource("testresource", test_items)

        # Check that we retireve the items on a GET call
        response = requests.get(api_url('testresource/?where={"testpk": {"$gte": 10}}'))
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("_items")
        expect(sorted(data["_items"])).to.have.length_of(40)

    def testSort(self):
        """ Test ?sort query with with mongo syntax. """
        test_items = [{"testpk": i} for i in range(50)]

        self.eve_mocker.set_resource("testresource", test_items)

        # Check that we retireve the items on a GET call
        response = requests.get(api_url('testresource/?sort={"testpk": 1}'))
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("_items")
        expect(data["_items"][0]).to.equal({"testpk": 0})

    def testSortDesc(self):
        test_items = [{"testpk": i} for i in range(50)]

        self.eve_mocker.set_resource("testresource", test_items)

        response = requests.get(api_url('testresource/?sort={"testpk": -1}'))
        data = response.json()
        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("_items")
        expect(data["_items"][0]).to.equal({"testpk": 49})

    def testSortDescWithWhere(self):
        test_items = [{"testpk": i} for i in range(50)]

        self.eve_mocker.set_resource("testresource", test_items)

        response = requests.get(api_url('testresource/?sort={"testpk": -1}&where={"testpk": {"$lte": 30}}'))
        data = response.json()
        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("_items")
        expect(data["_items"][0]).to.equal({"testpk": 30})

    def testSetResourceNoPk(self):
        """ Set a resource item without PK should raise an Exception. """
        # No pk for the item should raise an Exception
        falsy_items = [{"content": "content1"}]
        set_resource = self.eve_mocker.set_resource

        expect(set_resource).when.called_with("testresource",
                                              falsy_items).should.throw(Exception)

    def testQueryData(self):
        """ Test if mongo query syntax works, testing the raw query_data """
        test_data = [{"testpk": i} for i in range(50)]
        res = query_data(test_data, {"testpk": 10})

        expect(res).to.have.length_of(1)
        expect(res[0]).to.equal(test_data[10])

        res = query_data(test_data, {"testpk": {"$gte": 10}})
        expect(res).to.have.length_of(40)

        res = query_data(test_data, {"testpk": {"$gte": 10, "$lte": 15}})
        expect(res).to.have.length_of(6)

        res = query_data(test_data, {"badkey": {"$gte": 10, "$lte": 15}})
        expect(res).to.have.length_of(0)

        res = query_data(test_data, {"testpk": {"$in": [1, 2, 3, 4, 5]}})
        expect(res).to.have.length_of(5)

        res = query_data(test_data, {"testpk": {"$nin": [1, 2, 3, 4, 5]}})
        expect(res).to.have.length_of(45)

        res = query_data(test_data, {"testpk": {"$ne": 10}})
        expect(res).to.have.length_of(49)

        res = query_data(test_data, {"testpk": {"$gt": 10}})
        expect(res).to.have.length_of(39)

        res = query_data(test_data, {"testpk": {"$lt": 10}})
        expect(res).to.have.length_of(10)

    def testContextManager(self):
        """ Test EveMocker within a context manager. """
        with EveMocker("http://myapi.com/api/"):
            response = requests.get("http://myapi.com/api/mymodel")
            expect(response.status_code).to.equal(200)
            expect(response.json()).to.equal({"_items": []})


if __name__ == '__main__':
    unittest.main()

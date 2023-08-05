# -*- coding: utf-8 -*-

import unittest
import boto

TABLE_NAME1 = 'Table-HR'
TABLE_NAME2 = 'Table-H'
TABLE_NAME_404 = 'Waldo'
TABLE_RT = 45
TABLE_WT = 123
TABLE_RT2 = 10
TABLE_WT2 = 10
TABLE_HK_NAME = u'hash_key'
TABLE_HK_TYPE = u'N'
TABLE_RK_NAME = u'range_key'
TABLE_RK_TYPE = u'S'

HK_VALUE1 = u'123'
HK_VALUE2 = u'456'
HK_VALUE3 = u'789'
RK_VALUE1 = u'Waldo-1'
RK_VALUE2 = u'Waldo-2'
RK_VALUE3 = u'Waldo-3'
RK_VALUE4 = u'Waldo-4'
RK_VALUE5 = u'Waldo-5'


ITEM1 = {
    TABLE_HK_NAME: {TABLE_HK_TYPE: HK_VALUE1},
    TABLE_RK_NAME: {TABLE_RK_TYPE: RK_VALUE1},
    u'relevant_data': {u'S': u'tata'},
}
ITEM2 = {
    TABLE_HK_NAME: {TABLE_HK_TYPE: HK_VALUE1},
    TABLE_RK_NAME: {TABLE_RK_TYPE: RK_VALUE2},
    u'relevant_data': {u'S': u'tete'},
}
ITEM3 = {
    TABLE_HK_NAME: {TABLE_HK_TYPE: HK_VALUE2},
    TABLE_RK_NAME: {TABLE_RK_TYPE: RK_VALUE3},
    u'relevant_data': {u'S': u'titi'},
}
ITEM4 = {
    TABLE_HK_NAME: {TABLE_HK_TYPE: HK_VALUE2},
    TABLE_RK_NAME: {TABLE_RK_TYPE: RK_VALUE4},
    u'relevant_data': {u'S': u'toto'},
}
ITEM5 = {
    TABLE_HK_NAME: {TABLE_HK_TYPE: HK_VALUE3},
    TABLE_RK_NAME: {TABLE_RK_TYPE: RK_VALUE5},
    u'relevant_data': {u'S': u'tutu'},
}

# Please note that most query features are not yet implemented hence not tested
class TestBatchWriteItem(unittest.TestCase):
    def setUp(self):
        from ddbmock.database.db import dynamodb
        from ddbmock.database.table import Table
        from ddbmock.database.key import PrimaryKey

        dynamodb.hard_reset()

        hash_key = PrimaryKey(TABLE_HK_NAME, TABLE_HK_TYPE)
        range_key = PrimaryKey(TABLE_RK_NAME, TABLE_RK_TYPE)

        self.t1 = Table(TABLE_NAME1, TABLE_RT, TABLE_WT, hash_key, range_key)
        self.t2 = Table(TABLE_NAME2, TABLE_RT, TABLE_WT, hash_key, None)

        dynamodb.data[TABLE_NAME1]  = self.t1
        dynamodb.data[TABLE_NAME2]  = self.t2

        self.t1.put(ITEM1, {})
        self.t2.put(ITEM4, {})

    def tearDown(self):
        from ddbmock.database.db import dynamodb
        from ddbmock import clean_boto_patch
        dynamodb.hard_reset()
        clean_boto_patch()

    def test_batch_write_item_nominal(self):
        from ddbmock import connect_boto_patch
        from ddbmock.database.db import dynamodb

        db = connect_boto_patch()

        expected = {
            "Responses": {
                TABLE_NAME1: {
                    "ConsumedCapacityUnits": 3
                },
                TABLE_NAME2: {
                    "ConsumedCapacityUnits": 2
                }
            }
        }

        ret = db.layer1.batch_write_item({
            TABLE_NAME1: [
                {
                    u"DeleteRequest": {
                        u"Key": {
                            u"HashKeyElement": {TABLE_HK_TYPE: HK_VALUE1},
                            u"RangeKeyElement": {TABLE_RK_TYPE: RK_VALUE1},
                        },
                    },
                },
                {u"PutRequest": {u"Item": ITEM2}},
                {u"PutRequest": {u"Item": ITEM3}},
            ],
            TABLE_NAME2: [
                {
                    u"DeleteRequest": {
                        u"Key": {
                            u"HashKeyElement": {TABLE_HK_TYPE: HK_VALUE2},
                        },
                    },
                },
                {u"PutRequest": {u"Item":ITEM5}},
            ],
        })

        self.assertEqual(expected, ret)

    def test_batch_write_item_table_404(self):
        from ddbmock import connect_boto_patch
        from ddbmock.database.db import dynamodb
        from boto.exception import BotoServerError

        db = connect_boto_patch()

        self.assertRaises(BotoServerError, db.layer1.batch_write_item, {
            TABLE_NAME_404: [
                {
                    u"DeleteRequest": {
                        u"Key": {
                            u"HashKeyElement": {TABLE_HK_TYPE: HK_VALUE1},
                            u"RangeKeyElement": {TABLE_RK_TYPE: RK_VALUE1},
                        },
                    },
                },
                {u"PutRequest": {u"Item": ITEM2}},
                {u"PutRequest": {u"Item": ITEM3}},
            ],
            TABLE_NAME2: [
                {
                    u"DeleteRequest": {
                        u"Key": {
                            u"HashKeyElement": {TABLE_HK_TYPE: HK_VALUE2},
                        },
                    },
                },
                {u"PutRequest": {u"Item":ITEM5}},
            ],
        })

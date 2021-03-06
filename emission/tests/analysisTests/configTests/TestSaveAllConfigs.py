# Standard imports
import unittest
import datetime as pydt
import logging
import json
import copy
import uuid

# Test imports
import emission.tests.common as etc
import emission.analysis.configs.config as eacc

import emission.net.usercache.abstract_usercache as enua
import emission.storage.timeseries.format_hacks.move_filter_field as estfm
import emission.analysis.intake.cleaning.filter_accuracy as eaicf
import emission.core.get_database as edb

class TestSaveAllConfigs(unittest.TestCase):
    def setUp(self):
        self.androidUUID = uuid.uuid4()
        self.iosUUID = uuid.uuid4()
        self.dummy_config = {'user_id': self.androidUUID,
                             'metadata': {
                                'key': 'config/sensor_config'
                              }, 'data': {
                                'is_duty_cycling': True
                              }
                            }
        logging.debug("androidUUID = %s, iosUUID = %s" % (self.androidUUID, self.iosUUID))

    def tearDown(self):
        edb.get_timeseries_db().remove({"user_id": self.androidUUID}) 
        edb.get_timeseries_db().remove({"user_id": self.iosUUID}) 
        edb.get_usercache_db().remove({"user_id": self.androidUUID}) 
        edb.get_usercache_db().remove({"user_id": self.iosUUID}) 
        edb.get_place_db().remove() 
        edb.get_trip_new_db().remove() 

    def testNoOverrides(self):
        tq = enua.UserCache.TimeQuery("write_ts", 1440658800, 1440745200)
        eacc.save_all_configs(self.androidUUID, tq)
        saved_entries = list(edb.get_usercache_db().find({'user_id': self.androidUUID, 'metadata.key': 'config/sensor_config'}))
        self.assertEqual(len(saved_entries), 0)

    def testOneOverride(self):
        cfg_1 = copy.copy(self.dummy_config)
        cfg_1['metadata']['write_ts'] = 1440700000
        edb.get_timeseries_db().insert(cfg_1)

        tq = enua.UserCache.TimeQuery("write_ts", 1440658800, 1440745200)
        eacc.save_all_configs(self.androidUUID, tq)
        saved_entries = list(edb.get_usercache_db().find({'user_id': self.androidUUID, 'metadata.key': 'config/sensor_config'}))
        self.assertEqual(len(saved_entries), 1)
        logging.debug(saved_entries[0])
        self.assertEqual(saved_entries[0]['data']['is_duty_cycling'], cfg_1['data']['is_duty_cycling'])

    def testTwoOverride(self):
        cfg_1 = copy.copy(self.dummy_config)
        cfg_1['metadata']['write_ts'] = 1440700000
        edb.get_timeseries_db().insert(cfg_1)

        cfg_2 = copy.copy(self.dummy_config)
        cfg_2['metadata']['write_ts'] = 1440710000
        cfg_2['data']['is_duty_cycling'] = False
        edb.get_timeseries_db().insert(cfg_2)

        tq = enua.UserCache.TimeQuery("write_ts", 1440658800, 1440745200)
        eacc.save_all_configs(self.androidUUID, tq)
        saved_entries = list(edb.get_usercache_db().find({'user_id': self.androidUUID, 'metadata.key': 'config/sensor_config'}))
        self.assertEqual(len(saved_entries), 1)
        logging.debug(saved_entries[0])
        self.assertEqual(saved_entries[0]['data']['is_duty_cycling'], cfg_2['data']['is_duty_cycling'])

    def testOldOverride(self):
        cfg_1 = copy.copy(self.dummy_config)
        cfg_1['metadata']['write_ts'] = 1440500000
        edb.get_timeseries_db().insert(cfg_1)

        cfg_2 = copy.copy(self.dummy_config)
        cfg_2['metadata']['write_ts'] = 1440610000
        edb.get_timeseries_db().insert(cfg_2)

        tq = enua.UserCache.TimeQuery("write_ts", 1440658800, 1440745200)
        eacc.save_all_configs(self.androidUUID, tq)
        saved_entries = list(edb.get_usercache_db().find({'user_id': self.androidUUID, 'metadata.key': 'config/sensor_config'}))
        self.assertEqual(len(saved_entries), 0)
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

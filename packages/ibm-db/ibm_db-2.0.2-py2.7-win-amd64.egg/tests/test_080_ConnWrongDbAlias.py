# 
#  Licensed Materials - Property of IBM
#
#  (c) Copyright IBM Corp. 2007-2008
#

import unittest, sys
import ibm_db
import config
from testfunctions import IbmDbTestFunctions

class IbmDbTestCase(unittest.TestCase):

  def test_080_ConnWrongDbAlias(self):
    obj = IbmDbTestFunctions()
    obj.assert_expect(self.run_test_080)

  def run_test_080(self):
    try:
      conn = ibm_db.connect("x", config.user, config.password)
      print "??? No way."
    except:
      print ibm_db.conn_error()
 
    #if conn:
    #  print "??? No way."
    #else:
    #  print ibm_db.conn_error()

#__END__
#__LUW_EXPECTED__
#08001
#__ZOS_EXPECTED__
#08001
#__SYSTEMI_EXPECTED__
#08001
#__IDS_EXPECTED__
#08001

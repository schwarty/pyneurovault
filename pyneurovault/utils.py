#!/usr/bin/env python

"""

utils: part of the pyneurovault package

pyneurovault: a python wrapped for the neurovault api

"""

import os
import json
import errno
import urllib2
import pandas
import numpy as np
from pandas.io.json import read_json
from urllib2 import Request, urlopen, HTTPError

__author__ = ["Poldracklab","Chris Filo Gorgolewski","Gael Varoquaux","Vanessa Sochat"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015/01/16 $"
__license__ = "BSD"


# Get standard brains

def get_standard_brain():
  cwd = os.path.abspath(os.path.split(__file__)[0])
  return "%s/MNI152_T1_2mm_brain.nii.gz" %(cwd)

def get_standard_mask():
  cwd = os.path.abspath(os.path.split(__file__)[0])
  return "%s/MNI152_T1_2mm_brain_mask.nii.gz" %(cwd)


# File operations 

def mkdir_p(path):
  try:
      os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else: raise

def get_url(url):
  request = Request(url)
  response = urlopen(request)
  return response.read()

'''Return general json'''
def get_json(url):
    json_single = get_url(url)
    json_single = json.loads(json_single.decode("utf-8"))
    if json_single["count"] == 1:
        return json_single["results"]
    else:
        print "Found %s results." %(json_single["count"])    
        json_all = json_single["results"]
        while json_single["next"] is not None:
             print "Retrieving %s" %(json_single["next"])
             try:
                 json_single = get_url(json_single["next"])
                 json_single = json.loads(json_single.decode("utf-8"))
                 json_all = json_all + json_single['results']
             except HTTPError:
                 print "Cannot get, retrying"
        return json_all 

'''Return paginated json data frame, for images and collections'''
def get_json_df(data_type,pks=None,limit=1000):
    json_all = list()
    if pks==None:  # May not be feasible call if database is too big
         url = "http://neurovault.org/api/%s/?limit=%s&format=json" %(data_type,limit)
         json_all = pandas.DataFrame(get_json(url))

    else:
        if isinstance(pks,str): pks = [pks]
        if isinstance(pks,int): pks = [pks]
        json_all = "["
        for p in range(0,len(pks)):
            pk = pks[p]
            print "Retrieving %s %s..." %(data_type[0:-1],pk)
            try:
                tmp = get_url("http://neurovault.org/api/images/%s/?format=json" %(pk))
                if p!=0:
                    json_all = "%s,%s" %(json_all,tmp)
                else:
                    json_all = "%s%s" %(json_all,tmp)
            except:
                print "Cannot retrieve %s %s, skipping." %(data_type[0:-1],pk)
            
        json_all = "%s]" %(json_all)
        json_all = pandas.DataFrame(json.loads(json_all.decode("utf-8")))
    return json_all

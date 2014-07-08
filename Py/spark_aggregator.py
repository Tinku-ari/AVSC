"""SimpleApp.py"""
import numpy as np
from operator import add
from pyspark import SparkConf, SparkContext
from collections import defaultdict

conf = (SparkConf()
         .setMaster("local")
         .setAppName("My app")
         .set("spark.executor.memory", "8g")
         .set("spark.storage.memoryFraction","0.3")
)
sc = SparkContext(conf = conf)


directory = "/mnt/data/reducedpart/"  # Should be some file on your system
ct_distinct=np.zeros(4)
cust_dept=defaultdict(int)
for i in xrange(31):
     counter='%02d'%(i)
     infile=directory+'reduced_part_'+str(counter) #'trainHistory.csv'
     print infile
     logData = sc.textFile(infile)
     #line= logData.flatMap(lambda x:x.split('\n'))
     entries_by_line= logData.map(lambda x:x.split(','))  #.take(2000000)
     key_val=entries_by_line.map(lambda x:(x[0],x[2]))
     ct_keyval=key_val.map(lambda x:(x,1)).reduceByKey(add)
     for k,v in ct_keyval.collect():
         cust_dept[k]+=v
     #logData.unpersist()
     #print cust_dept.take(10)
     #if j==0: ct_distinct[j-2]-=1
print len(cust_dept.keys())
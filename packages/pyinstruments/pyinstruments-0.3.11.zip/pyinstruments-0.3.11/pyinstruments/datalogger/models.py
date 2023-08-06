from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import time
from datetime import datetime
import pandas

NaN = float('NaN')

class Sensor(models.Model):
    name = models.CharField(max_length = 255)
    description = models.CharField(max_length = 2047, blank=True)
    
    def __unicode__(self):
        return self.name

class MeasurementPoint(models.Model):
    
    def __unicode__(self):
        return str(self.sensor) + ':'+ str(self.value)
    
    sensor = models.ForeignKey(Sensor,
                               related_name='measurement_points', \
                               blank=True)
    value = models.FloatField()
    time = models.FloatField(db_index=True)
    
    class Meta: 
        ordering = ['time']
        get_latest_by = 'time'

    @property
    def sensor_name(self):
        return self.sensor.name
    
    @sensor_name.setter
    def sensor_name(self, name):
        try:
            self.sensor = Sensor.objects.get(name=name)
        except ObjectDoesNotExist:
            new_sensor = Sensor(name=name)
            new_sensor.save()
            self.sensor = new_sensor
        return name

# all data to be logged are to be derived objects from SensingDevice, 
# which provides basic functionality such as storing and retrieving data   

class SensingDevice(object):
    def __init__(self, name, timeout = 30, description = '', minval = 0.0, maxval = 100000.0):
        sense = Sensor.objects.get_or_create(name = name)
        self.sensorlog = sense[0]
        if sense[1] is False and description != ''  :
            self.sensorlog.description = description
            self.sensorlog.save()
        self.MINVAL = minval
        self.MAXVAL = maxval
        self.val = NaN
        self.active = False
        self.timeout = timeout
        self.name = name
        
    def now(self):
        return time.time()
    
    def log(self, value, mtime = -1.):
        if mtime == -1.:
            mtime = self.now()
        self.lastpoint = MeasurementPoint(sensor = self.sensorlog,\
                                                 value = value, \
                                                 time = mtime)
        if value >= self.MINVAL and value <= self.MAXVAL:
            self.lastpoint.save()
        else:
            print "Measurement Error: value " + str(value) + " of sensor "+\
                    self.sensorlog.name + " lies out of defined range. \n"
        return self.lastpoint
    
    #return last point as pandas Series
    #def getlastpoint(self):
    #    return self.toSeries(\
    #        [MeasurementPoint.objects.filter(sensor = self.sensorlog).latest()])
    
    #return last point as tuple
    def getlastpoint(self):
        val = MeasurementPoint.objects.filter(\
                                sensor = self.sensorlog).latest()
        return {'value': val.value, \
                'time': val.time, \
                'age': self.now()-val.time  }

    def getlastvalue(self):
        val = MeasurementPoint.objects.filter(\
                                sensor = self.sensorlog).latest()
        return val.value
    
    def getlastgoodvalue(self):
        val = MeasurementPoint.objects.filter(\
                                sensor = self.sensorlog).latest()
        if self.now()           -val.time < self.timeout:
            return val.value
        else:
            return NaN
    
    def getallpoints(self):
        return self.toSeries(\
                MeasurementPoint.objects.filter(sensor = self.sensorlog)) 

    def getallpointssince(self, sincetime):
        if sincetime <0:
            sincetime+=self.now()
        return self.toSeries(\
                MeasurementPoint.objects.filter(sensor = self.sensorlog,\
                                                    time__gt = sincetime)) 

    def getallpointsrange(self, starttime, stoptime=NaN):
        if stoptime == NaN:
            stoptime = self.now()
        if starttime < 0:
            starttime+=self.now()
            stoptime+=self.now()
        return self.toSeries(\
                MeasurementPoint.objects.filter(sensor = self.sensorlog,\
                                      time__range = (starttime,stoptime))) 
 
    def getallpointsaround(self, time = NaN, offset = NaN):

        if offset == NaN:
            offset = timeout

        if time == NaN:
            time=self.now()
        elif time < 0:
            time+=self.now()
        starttime = time-offset
        stoptime = time+offset
        return self.toSeries(\
                MeasurementPoint.objects.filter(sensor = self.sensorlog,\
                                      time__range = (starttime,stoptime))) 
         
    def toSeries(self, res):
        return pandas.Series(data = [i.value for i in res],\
                index = [datetime.fromtimestamp(k.time) for k in res],\
                name = self.sensorlog.name)
    
    def plot(self,lastseconds=-1.):
        if lastseconds == -1:
            since = 0
        else:
            since = self.now()-lastseconds
        df = pandas.DataFrame(self.getallpointssince(since))
        df.plot(style ='k.')
 
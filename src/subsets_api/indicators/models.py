from djongo import models
from django.utils import timezone

# Create your models here.

class IndicatorType(models.Model):
    _id = models.ObjectIdField()
    name = models.TextField()
    
class Crop(models.Model):
    _id = models.ObjectIdField()
    name = models.CharField(max_length=100)

class Indicator(models.Model):
    _id = models.ObjectIdField()
    name = models.TextField()
    prefix = models.TextField()
    indicator_type = models.ForeignKey('IndicatorType', models.DO_NOTHING, db_column='indicator_type')
    crops = models.ArrayField(
        model_container = Crop
    )

class Accession(models.Model):
    _id = models.ObjectIdField(primary_key= True)
    name = models.TextField(null = True)
    number = models.TextField(null = True)
    acq_date = models.IntegerField(null = True)
    aegis = models.IntegerField(null = True)
    available = models.IntegerField(null = True)
    coll_date = models.IntegerField(null = True)
    countryOfOrigin_code3 = models.TextField(null = True)
    countryOfOrigin_name = models.TextField(null = True)
    countryOfOrigin_region_name = models.TextField(null = True)
    samp_stat = models.IntegerField(null = True)
    crop_name = models.TextField(null = True)
    doi = models.TextField(null = True)
    historic = models.IntegerField(null = True)
    id = models.IntegerField(null = True)
    institute_fullname = models.TextField(null = True)
    institute_acronym = models.TextField(null = True)
    geo_lon = models.DecimalField(max_digits = 5, decimal_places = 2, null = True)
    geo_lat = models.DecimalField(max_digits = 5, decimal_places = 2, null = True)
    geo_ele = models.DecimalField(max_digits = 5, decimal_places = 2, null = True)
    cellid = models.IntegerField()

class IndicatorPeriod(models.Model):
    _id = models.ObjectIdField()
    indicator = models.ForeignKey('Indicator', models.DO_NOTHING, db_column='indicator')
    period = models.TextField()    

class IndicatorValue(models.Model):
    cellid = models.IntegerField()
    indicator_period = models.ForeignKey('IndicatorPeriod', models.DO_NOTHING, db_column='indicator_period')
    month = models.IntegerField()
    value = models.DecimalField(max_digits = 5, decimal_places = 2, null = True)
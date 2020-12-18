from djongo import models
from django.utils import timezone

# Create your models here.


class IndicatorKind(models.Model):
    _id = models.ObjectIdField()
    name = models.TextField()

class Indicator(models.Model):
    _id = models.ObjectIdField()
    indicator_kind = models.ForeignKey('IndicatorKind', models.DO_NOTHING, db_column='indicator_kind')
    name = models.TextField()

class Crop(models.Model):
    _id = models.ObjectIdField()
    name = models.TextField()
    indicators = models.JSONField()

class Institution(models.Model):
    _id = models.ObjectIdField()
    id_genesys = models.TextField()
    name = models.TextField()

class Accession(models.Model):
    _id = models.ObjectIdField(primary_key= True)
    accessionName = models.TextField(null = True)
    accessionNumber = models.TextField(null = True)
    acquisitionDate = models.IntegerField(null = True)
    aegis = models.IntegerField(null = True)
    available = models.IntegerField(null = True)
    coll_collDate = models.IntegerField(null = True)
    countryOfOrigin_code3 = models.TextField(null = True)
    countryOfOrigin_name = models.TextField(null = True)
    countryOfOrigin_region_name = models.TextField(null = True)
    sampStat = models.IntegerField(null = True)
    crop_name = models.TextField(null = True)
    doi = models.TextField(null = True)
    historic = models.IntegerField(null = True)
    id = models.IntegerField(null = True)
    institute_fullName = models.TextField(null = True)
    institute_acronym = models.TextField(null = True)
    geo_longitude = models.DecimalField(max_digits = 5, decimal_places = 2, null = True)
    geo_latitude = models.DecimalField(max_digits = 5, decimal_places = 2, null = True)
    geo_elevation = models.DecimalField(max_digits = 5, decimal_places = 2, null = True)

class IndicatorValue(models.Model):
    _id = models.ObjectIdField()
    indicator = models.ForeignKey('Indicator', models.DO_NOTHING, db_column='indicator')
    type = models.TextField()
    name = models.TextField()

class Stats(models.Model):
    _id = models.ObjectIdField()
    indicator_value = models.ForeignKey('IndicatorValue', models.DO_NOTHING, db_column='indicator_value')
    median = models.DecimalField(max_digits = 5, decimal_places = 5)
    mean = models.DecimalField(max_digits = 5, decimal_places = 5)
    quartils = models.DecimalField(max_digits = 5, decimal_places = 5)
    percentil_5 = models.DecimalField(max_digits = 5, decimal_places = 5)
    percentil_95 = models.DecimalField(max_digits = 5, decimal_places = 5)
    desv_stand = models.DecimalField(max_digits = 5, decimal_places = 5)

class BiologicalStatus(models.Model):
    _id = models.ObjectIdField()
    id_mcpd = models.IntegerField()
    name = models.TextField()
    


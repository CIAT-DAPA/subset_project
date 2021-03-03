from djongo import models
from django import forms
from django.utils import timezone

# Create your models here.

class IndicatorType(models.Model):
    _id = models.ObjectIdField()
    name = models.TextField()

    def __str__(self):
        return self.name
    
class Crop(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name
    
    class Meta:
        abstract = True

class Crops(Crop):
    _id = models.ObjectIdField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'indicators_crop'


class CropForm(forms.ModelForm):
    
    class Meta:
        model = Crop
        fields = (
         'name',
        )

class Indicator(models.Model):
    _id = models.ObjectIdField()
    name = models.TextField()
    pref = models.TextField()
    indicator_type = models.ArrayReferenceField(to=IndicatorType, on_delete=models.CASCADE)
    crop = models.ArrayField(
        model_container=Crop,
        model_form_class=CropForm
    )

class Accession(models.Model):
    _id = models.ObjectIdField(primary_key= True)
    name = models.TextField(null = True)
    number = models.TextField(null = True)
    acq_date = models.TextField(null = True)
    aegis = models.TextField(null = True)
    available = models.TextField(null = True)
    coll_date = models.TextField(null = True)
    country_code = models.TextField(null = True)
    country_name = models.TextField(null = True)
    country_region_name = models.TextField(null = True)
    samp_stat = models.TextField(null = True)
    crop_name = models.TextField(null = True)
    doi = models.TextField(null = True)
    historic = models.IntegerField(null = True)
    id = models.IntegerField(null = True)
    institute_fullname = models.TextField(null = True)
    institute_acronym = models.TextField(null = True)
    geo_lon = models.FloatField()
    geo_lat = models.FloatField()
    geo_ele = models.TextField()
    cellid = models.IntegerField()

class IndicatorPeriod(models.Model):
    _id = models.ObjectIdField()
    period = models.TextField()    
    indicator = models.ForeignKey('Indicator', models.DO_NOTHING, db_column='indicator')

class IndicatorValue(models.Model):
    _id = models.ObjectIdField()
    cellid = models.IntegerField(null= True)
    indicator_period = models.ForeignKey('IndicatorPeriod', models.DO_NOTHING, db_column='indicator_period', null= True)
    month = models.IntegerField()
    value = models.FloatField()
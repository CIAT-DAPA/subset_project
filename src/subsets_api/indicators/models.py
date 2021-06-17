from djongo import models
from django.db import models as mode
from django import forms
from django.utils import timezone

# Create your models here.


class IndicatorType(models.Model):
    _id = models.ObjectIdField()
    name = models.TextField()

    def __str__(self):
        return self.name


class Crop(models.Model):
    _id = models.ObjectIdField()
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
    indicator_type = models.ArrayReferenceField(
        to=IndicatorType, on_delete=models.CASCADE)
    crop = models.ArrayField(
        model_container=Crop,
        model_form_class=CropForm
    )


class Accession(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    name = models.TextField(null=True, db_index=True)
    number = models.TextField(null=True)
    acq_date = models.TextField(null=True)
    aegis = models.TextField(null=True)
    available = models.TextField(null=True)
    coll_date = models.TextField(null=True)
    country_code = models.TextField(null=True)
    country_name = models.TextField(null=True, db_index=True)
    country_region_name = models.TextField(null=True)
    samp_stat = models.TextField(null=True, db_index=True)
    crop = models.ForeignKey(
        'Crops', on_delete=models.PROTECT, db_column='crop', db_index=True)
    doi = models.TextField(null=True)
    historic = models.IntegerField(null=True)
    id = models.IntegerField(null=True, db_index=True)
    institute_fullname = models.TextField(null=True)
    institute_acronym = models.TextField(null=True, db_index=True)
    geo_lon = models.FloatField(null=True)
    geo_lat = models.FloatField(null=True)
    geo_ele = models.TextField(null=True)
    cellid = models.IntegerField(db_index=True)
    taxonomy_genus = models.TextField(db_index=True)
    taxonomy_sp_author = models.TextField(db_index=True)
    taxonomy_species = models.TextField(db_index=True)
    taxonomy_taxon_name = models.TextField(db_index=True)

    class Meta:
        indexes = [
            mode.Index(fields=['crop', 'name', 'country_name',
                               'institute_acronym', 'samp_stat', ]),
            mode.Index(fields=['crop', 'name', ]),
            mode.Index(fields=['crop', 'country_name', ]),
            mode.Index(fields=['geo_lon', 'geo_lat', ]),
        ]


class IndicatorPeriod(models.Model):
    _id = models.ObjectIdField()
    period = models.TextField()
    indicator = models.ForeignKey(
        'Indicator', models.DO_NOTHING, db_column='indicator')


class IndicatorValue(models.Model):
    _id = models.ObjectIdField()
    cellid = models.IntegerField(null=True, db_index=True)
    indicator_period = models.ForeignKey(
        'IndicatorPeriod', on_delete=models.PROTECT, db_column='indicator_period', db_index=True)
    month1 = models.FloatField(db_index=True)
    month2 = models.FloatField(db_index=True)
    month3 = models.FloatField(db_index=True)
    month4 = models.FloatField(db_index=True)
    month5 = models.FloatField(db_index=True)
    month6 = models.FloatField(db_index=True)
    month7 = models.FloatField(db_index=True)
    month8 = models.FloatField(db_index=True)
    month9 = models.FloatField(db_index=True)
    month10 = models.FloatField(db_index=True)
    month11 = models.FloatField(db_index=True)
    month12 = models.FloatField(db_index=True)

    class Meta:
        indexes = [
            mode.Index(fields=['indicator_period', 'month1',
                               'month2', 'month3', 'month4', 'month5', 'month6', 'month7', 'month8', 'month9', 'month10', 'month11',
                               'month12', ]),
            mode.Index(fields=['indicator_period', 'month1',
                               'month2', 'month3', ]),
            mode.Index(fields=['indicator_period', 'month4',
                               'month5', 'month6', ]),
            mode.Index(fields=['indicator_period', 'month7',
                               'month8', 'month9', ]),
            mode.Index(fields=['indicator_period', 'month10',
                               'month11', 'month12', ]),
            mode.Index(fields=['indicator_period', 'month9',
                               'month10', 'month11', 'month12', 'month1', 'month2', 'month3' ]),
        ]
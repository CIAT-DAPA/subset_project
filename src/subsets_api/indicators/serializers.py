from rest_framework import serializers

# Local models
from .models import *


class IndicatorTypesSerializer(serializers.ModelSerializer):
    """ Serializers for indicators type"""
    class Meta:
        model = IndicatorType
        fields = '__all__'


class IndicatorsSerializer(serializers.ModelSerializer):
    """ Serializers for indicators """
    class Meta:
        model = Indicator
        fields = '__all__'


class IndicatorPeriodsSerializer(serializers.ModelSerializer):
    """ Serializers for indicators """
    indicator = IndicatorsSerializer(read_only=True)

    class Meta:
        model = IndicatorPeriod
        fields = '__all__'


class IndicatorValuesSerializer(serializers.ModelSerializer):
    """ Serializers for indicators """
    indicator_period = IndicatorPeriodsSerializer(read_only=True)

    class Meta:
        model = IndicatorValue
        #fields = ('month1')
        fields = ('cellid', 'month1', 'month2', 'month3', 'month4', 'month5', 'month6', 'month7',
                  'month8', 'month9', 'month10', 'month11', 'month12', '_id',  'indicator_period')
        read_only_fields = fields
        #fields = '__all__'

class IndicatorValueOnlySerializer(serializers.Serializer):
    month1 = serializers.FloatField(read_only=True)
    month2 = serializers.FloatField(read_only=True)
    month3 = serializers.FloatField(read_only=True)
    month4 = serializers.FloatField(read_only=True)   
    month5 = serializers.FloatField(read_only=True)   
    month6 = serializers.FloatField(read_only=True)   
    month7 = serializers.FloatField(read_only=True)   
    month8 = serializers.FloatField(read_only=True)   
    month9 = serializers.FloatField(read_only=True)   
    month10 = serializers.FloatField(read_only=True)   
    month11 = serializers.FloatField(read_only=True)   
    month12 = serializers.FloatField(read_only=True)   
    cellid = serializers.IntegerField(read_only=True)   


class CropsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crops
        #fields = '__all__'
        fields = ("name",)


class AccessionsSerializer(serializers.ModelSerializer):
    """ Serializers for accessions """
    crop = CropsSerializer(read_only=True)

    class Meta:
        model = Accession
        #fields = '__all__'
        fields = ("name", "number", "acq_date", "coll_date", "country_name", "samp_stat", "crop",
                    "institute_fullname", "institute_acronym", "geo_lon", "geo_lat", "geo_ele", 
                    "taxonomy_genus", "taxonomy_sp_author", "taxonomy_species", "taxonomy_taxon_name")

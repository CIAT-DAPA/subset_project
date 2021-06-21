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
        #fields = '__all__'


class CropsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crops
        fields = '__all__'


class AccessionsSerializer(serializers.ModelSerializer):
    """ Serializers for accessions """
    crop = CropsSerializer(read_only=True)

    class Meta:
        model = Accession
        fields = '__all__'

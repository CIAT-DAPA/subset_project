from rest_framework import serializers

#Local models
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

class AccessionsSerializer(serializers.ModelSerializer):
    """ Serializers for accessions """
    class Meta:
        model = Accession
        fields = '__all__'

class IndicatorPeriodsSerializer(serializers.ModelSerializer):
    """ Serializers for indicators """
    class Meta:
        model = Indicator
        fields = '__all__'

class IndicatorValuesSerializer(serializers.ModelSerializer):
    """ Serializers for indicators """
    class Meta:
        model = Indicator
        fields = '__all__'
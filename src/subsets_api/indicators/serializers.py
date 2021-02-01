from rest_framework import serializers

#Local models
from .models import *

class AccessionsSerializer(serializers.ModelSerializer):
    """ Serializers for accessions """
    class Meta:
        model = Accession
        fields = '__all__'

class CropsSerializer(serializers.ModelSerializer):
    """ Serializers for crops """
    class Meta:
        model = Crop
        fields = '__all__'

class BiologicalStatusSerializer(serializers.ModelSerializer):
    """ Serializers for biological status """
    class Meta:
        model = BiologicalStatus
        fields = '__all__'
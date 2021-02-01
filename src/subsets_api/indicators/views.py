from django.shortcuts import render
from rest_framework import viewsets, mixins, filters
from rest_framework.response import Response

#local models
from .models import *
from .serializers import *

# Create your views here.

class AccesionsViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """ ViewSet for Accessions """
    search_fields = ['countryOfOrigin_name', 'institute_fullName', 'institute_acronym']
    filter_backends = (filters.SearchFilter,)
    queryset = Accession.objects.all()
    serializer_class = AccessionsSerializer

class AccesionsByBiologicalStatusViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """ ViewSet for Accessions by Biological Status """
    queryset = BiologicalStatus.objects.all()
    serializer_class = BiologicalStatusSerializer
    def list(self, request, *args, **kwargs):
        name = self.kwargs['name']
        biologicalStatus = BiologicalStatus.objects.filter(name=name)
        serialier = BiologicalStatusSerializer(biologicalStatus, many=True)
        id_biological  = 0
        for e in biologicalStatus:
            id_biological = e.id_mcpd
        accessions = Accession.objects.filter(sampStat=id_biological)
        serialzer = AccessionsSerializer(accessions, many=True)
        return Response(serialzer.data)

class AccesionsByIdViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """ ViewSet for Accessions by ID """
    queryset = Accession.objects.all()
    serializer_class = AccessionsSerializer
    def list(self, request, *args, **kwargs):
        id = self.kwargs['id']
        accessions = Accession.objects.filter(id=id)
        serialier = AccessionsSerializer(accessions, many=True)
        return Response(serialier.data)

class AccesionsByCoordinatesViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """ ViewSet for Accessions by coordinates """
    queryset = Accession.objects.all()
    serializer_class = AccessionsSerializer
    def list(self, request, *args, **kwargs):
        lon = self.kwargs['lon']
        lat = self.kwargs['lat']
        accessions = Accession.objects.filter(geo_longitude=lon, geo_latitude= lat)
        serialier = AccessionsSerializer(accessions, many=True)
        return Response(serialier.data)

class CropsViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """ ViewSet for Crops """
    serializer_class = CropsSerializer
    queryset = Crop.objects.all()
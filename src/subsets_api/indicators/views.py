from django.shortcuts import render
from rest_framework import viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
import numpy as np

# local models
from .models import *
from .serializers import *
from .scripts import *


""" class IndicatorViewSet(generics.ListAPIView):
    def get_queryset(self):
        query_params = self.request.query_params
        indicators = query_params.get('indicators', None)

        indicatorParams = []
        if indicators is not None:
            for indicators in indicators.split['|']:
                indicatorParams.append(str(indicators))
        if indicators is not None:
            queryset_list = Indicator.object.all()
            queryset_list = queryset_list.filter(pref__in=indicatorParams)
            return queryset_list

class IndicatorValueViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    queryset = IndicatorValue.objects.all()
    serializer_class = IndicatorValuesSerializer
    def list(self, request, *args, **kwargs):
        value = self.kwargs['value']
        indicator_value = IndicatorValue.objects.filter(value = value)
        serialier = IndicatorValuesSerializer(indicator_value, many=True)
        return Response(serialier.data) """

""" class AccessionByIdViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    queryset = Accession.objects.all()
    serializer_class = AccessionsSerializer

    def list(self, request, *args, **kwargs):
        id = self.kwargs['id']
        accessions = self.queryset.filter(id = id)
        serializer = self.serializer_class(accessions, many=True)
        print(id)
        return Response(serializer.data) """

class AccessionsList(mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    queryset = Accession.objects.all()
    serializer_class = AccessionsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['crop_name', 'name', 'country_name', 'samp_stat', 'institute_fullname', 'institute_acronym']

class CropList(mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    queryset = Crops.objects.all()
    print(queryset)
    serializer_class = CropsSerializer

class IndicatorViewSet(mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    """ View to query indciators """
    queryset = Indicator.objects.all()
    serializer_class = IndicatorsSerializer

    def list(self, request, *args, **kwargs):
        indicator = self.queryset
        serializer = self.serializer_class(indicator, many=True)
        #print(getAccessions(id_accession))
        return Response(serializer.data)


class IndicatorPostViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    """ View to query indciators """
    queryset = Accession.objects.all()
    serializer_class = AccessionsSerializer

    def create(self, request, *args, **kwargs):

        #request indicator data
        month = self.request.data['month']
        value = self.request.data['value']
        indicator = self.request.data['indicator']
        period = self.request.data['period']
        lst = []

        if (month == ""):
            queryIndicator = IndicatorValue.objects.filter(
                value__lte=value)
            for value in queryIndicator:
                accessions = self.queryset.filter(cellid=value.cellid)
                for acces in accessions:
                    lst.append(acces)
            serializer = self.serializer_class(lst, many=True)
            return Response(serializer.data)
        #indicator = Indicator.objects.filter()
        if (month != "") and (period != ""):
            #indicator queryset 
            print(indicator)
            indicator_qs = Indicator.objects.filter(pref=indicator).first()
            #indicator_period queryset
            indicator_period_qs = IndicatorPeriod.objects.filter(indicator=indicator_qs._id, period=period).first()
            print(indicator_period_qs._id)
            #indicator_value queryset
            min_value = float(value[0])
            max_value = float(value[1])
            print(min_value)
            queryIndicator = IndicatorValue.objects.filter(
                value__range=(min_value, max_value), month=month, indicator_period=indicator_period_qs._id)
            #iterating indicator_value queryset
            for value in queryIndicator:
                #accessions queryset
                accessions = self.queryset.filter(cellid=value.cellid)
                for acs in accessions:
                    #adding accessions records to list
                    lst.append(acs)
            #accessions serializer
            serializer = self.serializer_class(lst, many=True)
            return Response(serializer.data)

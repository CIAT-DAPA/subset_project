from django.shortcuts import render
from rest_framework import viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework import status
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

class AccessionsList(mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    queryset = Accession.objects.all()
    serializer_class = AccessionsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['crop_name', 'name', 'country_name', 'samp_stat', 'institute_fullname', 'institute_acronym', 'country_name']

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

        # request indicator data
        month = self.request.data['month']
        value = self.request.data['value']
        indicator = self.request.data['indicator']
        period = self.request.data['period']
        lst = []
        lst_accessions = []
        lst_indicator_period = []
        lst_indicator = []
        indicator_qs = ''
        indicator_period_qs = ''

        if (month == ""):
            queryIndicator = IndicatorValue.objects.filter(
                value__lte=value)
            for value in queryIndicator:
                accessions = self.queryset.filter(cellid=value.cellid)
                for acces in accessions:
                    lst.append(acces)
            serializer = self.serializer_class(lst, many=True)
            return Response(serializer.data)
        # indicator = Indicator.objects.filter()
        if (month != ""):
            # indicator queryset
            indicator_qs = Indicator.objects.filter(name__in=indicator)
            # indicator_period queryset
            if "," in period:
                periods = period.split(",")
                for lst_ind in indicator_qs:
                    indicator_period_qs = IndicatorPeriod.objects.filter(
                            indicator=lst_ind._id, period__in=periods)
            elif "-" in period:
                for lst_ind in indicator_qs:
                    periods = period.split("-")
                    min_period = periods[0]
                    max_period = periods[1]
                    lst_indicator_period = IndicatorPeriod.objects.filter(
                        indicator=lst_ind._id, period__range=(min_period, max_period))

            # indicator_value queryset
            min_value = float(value[0])
            max_value = float(value[1])

            for pe in indicator_period_qs:
                queryIndicator = IndicatorValue.objects.filter(
                    value__range=(min_value, max_value), month__in=month, indicator_period=pe._id)
                for values in queryIndicator:
                    lst_accessions.append(values)
            # iterating indicator_value queryset
            lst_cellid = []
            for value in lst_accessions:
                # accessions queryset
                if value.cellid not in lst_cellid:
                    lst_cellid.append(value.cellid)
            # accessions serializer
            accessiones = self.queryset.filter(
                cellid__in=lst_cellid)
            serializer = self.serializer_class(accessiones, many=True)
            serializer_indicator_value = IndicatorValuesSerializer(
                lst_accessions, many=True)
            serializer_list = [serializer.data,
                               serializer_indicator_value.data]
            content = {
                'status': 1,
                'responseCode': status.HTTP_200_OK,
                'data': serializer_list,
            }
            return Response(content)

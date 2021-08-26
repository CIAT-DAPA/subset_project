from statistics import multimode
from django.core import paginator
from django.shortcuts import render
from rest_framework import viewsets, mixins, filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from django_filters import Filter, FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
import numpy as np
from itertools import chain
from django.http import HttpResponse
from django.core import serializers
from django.db.models import Count, query
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.http import JsonResponse
from bson import ObjectId
import json
from bson import json_util
import pandas as pd
import operator
from django.db.models import Q
from functools import reduce
from django_pandas.io import read_frame
from django.core.paginator import Paginator
from django.db.models import Prefetch
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.settings import api_settings

# local models
from .models import *
from .serializers import *
from .scripts import *
from .custom_indicators.custom_ind import *
from .multivariate_analysis.dbscan_analysis import *
from .mixins import MyPaginationMixin

import time
from django.db import connection


class AccessionsView(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    
    queryset = Accession.objects.all()
    serializer_class = AccessionsSerializer

    def create(self, request, *args, **kwargs):
        data = request.get_json()

        start = time.time()
        filter_clauses = [Q(**{filter + "__in": data[filter]})
                        for filter in data if len(data[filter]) > 0]
        print(filter_clauses)
        #accessions = Accession.objects((Q(crop__in = data["crop"])) & (Q(country_name__in = data["country_name"]))).select_related()
        accessions = Accession.objects(
            reduce(operator.and_, filter_clauses)).select_related()
        rows = len(accessions)
        end = time.time()
        print("Accessions: " + str(rows) + " time: " + str((end-start)*1000.0))

        start = time.time()
        result = [{"name": x.name,
                "number": x.number,
                "acq_date": x.acq_date,
                "coll_date": x.coll_date,
                "country_name": x.country_name,
                "institute_fullname": x.institute_fullname,
                "institute_acronym": x.institute_acronym,
                "crop": x.crop.name,
                "geo_lon": x.geo_lon,
                "geo_lat": x.geo_lat,
                "geo_ele": x.geo_ele,
                "taxonomy_genus": x.taxonomy_genus,
                "taxonomy_sp_author": x.taxonomy_sp_author,
                "taxonomy_species": x.taxonomy_species,
                "taxonomy_taxon_name": x.taxonomy_taxon_name,
                "cellid": x.cellid
                }
                for x in accessions]
        rows = len(result)
        end = time.time()
        print("Result " + str(rows) + " time: " + str((end-start)*1000.0))

        return Response(result)
        """ print(Accession.objects.all())
        passport_params = request.data['passport']
        crop_params = request.data['crop']
        passport = passport_params[0]
        crop = crop_params[0]
        queryset_crop = Crops.objects.filter(
            name__in=crop['names']).values_list("_id", flat=True)
        crop_par = [Q(**{'crop__in': list(queryset_crop)})]
        passport_clauses = [Q(**{filter: passport[filter]})
                            for filter in passport if len(passport[filter]) > 0]
        passport_clauses = crop_par + passport_clauses
        #queryset = self.queryset.filter(reduce(operator.and_, passport_clauses)).select_related("crop")
        queryset = Accession.objects.filter(reduce(operator.and_, passport_clauses)).select_related("crop")
        #print(queryset)
        #paginator = Paginator(queryset, 500)
        #page = paginator.page(1)
        #page = self.paginate_queryset(queryset)
        #if page is not None:
        #    serializer = self.serializer_class(page, many=True)
        #    return self.get_paginated_response(serializer.data)
        # return Response(que)
        return Response(self.serializer_class(queryset)) """


class CropList(mixins.CreateModelMixin,
               mixins.ListModelMixin,
               mixins.RetrieveModelMixin,
               mixins.UpdateModelMixin,
               viewsets.GenericViewSet):
    queryset = Crops.objects.all()
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
        return Response(serializer.data)


class IndicatorValViewSet(mixins.CreateModelMixin,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    """ View to query indciators """
    queryset = IndicatorValue.objects.all()
    serializer_class = IndicatorValuesSerializer

    def create(self, request, *args, **kwargs):
        #start = time.time()
        passport_params = request.data['passport']
        crop_params = request.data['crop']
        indicators_params = request.data['data']
        #minp = request.data['minp']
        #eps = request.data['eps']
        lst = []
        period = indicators_params[0]
        nMonths = 0
        nYears = 0
        for x in range(period['period'][0], period['period'][1] + 1):
            nMonths = nMonths + 12
            nYears = nYears + 1
        passport = passport_params[0]
        crop = crop_params[0]
        queryset_crop = Crops.objects.filter(
            name__in=crop['names']).values_list("_id", flat=True)
        crop_par = [Q(**{'crop__in': list(queryset_crop)})]
        passport_clauses = [Q(**{filter: passport[filter]})
                            for filter in passport if len(passport[filter]) > 0]
        passport_clauses = passport_clauses + \
            crop_par + [Q(**{'cellid__gt': 0})]
        queryset_cellids = Accession.objects.filter(
            reduce(operator.and_, passport_clauses)).select_related("crop").values_list('cellid', flat=True).distinct()
        print(queryset_cellids)
        cellid = [Q(**{'cellid__in': sorted(list(queryset_cellids))})]
        print(cellid)
        for prop in indicators_params:
            query_indicator = Indicator.objects.filter(
                name=prop['indicator_name']).first()
            print(query_indicator.name)
            # queryset to get indicators period selected
            query_period = IndicatorPeriod.objects.filter(
                period__range=prop['period'], indicator=query_indicator._id)
            for qp in query_period:
                # Loop to search the values for each indicator and period
                id_indicator_period = [Q(**{'indicator_period': qp._id})]
                print(id_indicator_period)
                # Build the query from parameters in the request
                filter_clauses = [Q(**{filter: prop[filter]})
                                  for filter in prop if "month" in str(filter)]
                finished = id_indicator_period + filter_clauses + cellid
                if finished:
                    queryset = IndicatorValue.objects.filter(
                        reduce(operator.and_, finished)).select_related('indicator_period').values('cellid', 'month1', 'month2', 'month3', 'month4', 'month5', 'month6', 'month7',
                                                                                                   'month8', 'month9', 'month10', 'month11', 'month12',  'indicator_period__period', 'indicator_period__indicator__name', 'indicator_period__indicator__pref')
                    print(queryset.count())
                    if (queryset.count() > 0):
                        for x in queryset.iterator():
                            lst.append(x)
        #serializer = IndicatorValuesSerializer(lst, many=True)
        serializer_list = {
            'data': lst}
       #analysis = dbscan_analysis(serializer_list,int(nMonths),1)
        #result = analysis.to_json(orient = "records")
        #parsed = json.loads(result)
        content = {
            'status': 1,
            'responseCode': status.HTTP_200_OK,
            'data': serializer_list,
        }
        """paginator = Paginator(queryset,500)
                    page = paginator.page(1)
                    for x in page:
                        lst.append(x)
        if len(lst) > 0:
            analysis = dbscan_analysis(serializer_list,12, nYears)
            result = analysis.to_json(orient="records")
            parsed = json.loads(result)
            serializer_list = {
                'data': serializer.data, 'multivariety': parsed} 
        content = {
            'status': 1,
            'responseCode': status.HTTP_200_OK,
            'data': serializer_list,
        }"""

        """ paginator = Paginator(queryset,500)
                    page = paginator.page(1)
                    #serializer = IndicatorValuesSerializer(page, many=True)
                    #print(serializer.data
                    for values in page:
                        lst.append(values)
                        if values.cellid not in lst_cellids:
                            lst_cellids.append(values.cellid)
                    lst_t.append(lst_cellids)
                lst_cellids = []
        a = set(lst_t[0]).intersection(*lst_t[1:])
        for i in lst:
            if i.cellid in a:
                lst_final.append(i)
        serializer = self.serializer_class(lst_final, many=True)
        serializer_list = {
            'data': serializer.data, 'cellids': lst_cellids}
        analysis = dbscan_analysis(serializer_list,int(months),1)
        result = analysis.to_json(orient = "records")
        parsed = json.loads(result)
        serializer_list = {
            'data': serializer.data, 'cellids': a, 'multivariety': parsed}
        content = {
            'status': 1,
            'responseCode': status.HTTP_200_OK,
            'data': serializer_list,
        } """
        """ serializer = self.serializer_class(lst, many=True)
        serializer_list = {
            'data': serializer.data, 'cellids': lst_cellids}
        content = {
            'status': 1,
            'responseCode': status.HTTP_200_OK,
            'data': serializer_list,
        } """
        # if filter_clauses:
        #queryset = queryset.filter(reduce(operator.and_, filter_clauses))
        # Searching indicators values
        """ print(filter_clauses)
                print(IndicatorValue.objects.filter(reduce(operator.and_, filter_clauses)).query)
                queryset = IndicatorValue.objects.filter(reduce(operator.and_, filter_clauses))
                for values in queryset:
                    lst.append(values)
                    if values.cellid not in lst_cellids:
                        lst_cellids.append(values.cellid)
                lst_t.append(lst_cellids)
                lst_cellids = [] """
        """ end = time.time()
        print("Checking parameters: ", str(end - start))
        start = time.time()
        a = set(lst_t[0]).intersection(*lst_t[1:])
        for i in lst:
            if i.cellid in a:
                lst_final.append(i) 
        end = time.time()
        print("Searching cell ids: ", str(end - start))
        start = time.time()
        serializer = self.serializer_class(lst_final, many=True)
        serializer_list = {
            'data': serializer.data, 'cellids': lst_cellids}
        end = time.time()
        print("Preparing data for dbscan: ", str(end - start))
        start = time.time()
        analysis = dbscan_analysis(serializer_list,12,1)
        end = time.time()
        print("DBscan: ", str(end - start))
        start = time.time()
        result = analysis.to_json(orient = "records")
        parsed = json.loads(result)
        serializer_list = {
            'data': serializer.data, 'cellids': a, 'multivariety': parsed}
        content = {
            'status': 1,
            'responseCode': status.HTTP_200_OK,
            'data': serializer_list,
        }
        end = time.time()
        print("Serialize output: ", str(end - start))
        start = time.time() """
        # return HttpResponse(json.dumps(lst), content_type='application/json')
        return Response(content)


@csrf_exempt
@api_view(('POST',))
def get_custom_indicator(request):
    """ Proccessing custom data """
    # value= request.POST['test']
    data = request.data['data']
    var = request.data['vars']
    data = data[:-1]
    df = pd.DataFrame(data)
    detail = calculate_summary(df, var)
    accessions = merge_data(df, 'IG', 'id')
    serializer = AccessionsSerializer(accessions, many=True)
    print(serializer.data)
    serializer_list = {
        'accessions': serializer.data, 'stats': detail}
    content = {
        'status': 1,
        'responseCode': status.HTTP_200_OK,
        'data': serializer_list,
    }
    return Response(content)


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
        data = self.request.data['data']
        lst_accessions = []
        lst_cellid = []
        for props in data:
            indicator_qs = Indicator.objects.filter(
                name=props['indicator']).first()
            indicator_period_qs = IndicatorPeriod.objects.filter(
                indicator=indicator_qs._id, period__range=props['period'])
            for ind_per in indicator_period_qs:
                queryIndicator = IndicatorValue.objects.filter(
                    value__range=[props['value']['minValue'], props['value']['highValue']], month__in=props['months'], indicator_period=ind_per._id)
                for ind_val in queryIndicator:
                    lst_accessions.append(ind_val)
                    if ind_val.cellid not in lst_cellid:
                        lst_cellid.append(ind_val.cellid)
        serializer_indicator_value = IndicatorValuesSerializer(
            lst_accessions, many=True)
        serializer_list = {
            'data': serializer_indicator_value.data, 'cellids': lst_cellid}
        content = {
            'status': 1,
            'responseCode': status.HTTP_200_OK,
            'data': serializer_list,
        }
        return Response(content)
        """ month = self.request.data['month']
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
                value__lte=value).iterator()
            for value in queryIndicator:
                accessions = self.queryset.filter(cellid=value.cellid)
                for acces in accessions:
                    lst.append(acces)
            serializer = self.serializer_class(lst, many=True)
            return Response(serializer.data)
        # indicator = Indicator.objects.filter()
        if (month != ""):
            # indicator queryset
            print(indicator)
            indicator_qs = Indicator.objects.filter(name__in=indicator)
            ind_list = list(indicator_qs)
            ind_list.sort(key=lambda indic: indicator.index(indic.name))
            # indicator_period queryset
            if "," in period:
                periods = period.split(",")
                for lst_ind in ind_list:
                    print(lst_ind._id)
                    indicator_period_qs = IndicatorPeriod.objects.filter(
                            indicator=lst_ind._id, period__in=periods)
                    lst_indicator_period.append(indicator_period_qs)

            elif "-" in period:
                periods = period.split("-")
                min_period = periods[0]
                max_period = periods[1]
                for lst_ind in ind_list:
                    indicator_period_qs = IndicatorPeriod.objects.filter(
                        indicator=lst_ind._id, period__range=(min_period, max_period))

            # indicator_value queryset
            min_value = float(value[0])
            max_value = float(value[1])

            for pe in lst_indicator_period:
                for p in pe:
                    print(p.period)
                    queryIndicator = IndicatorValue.objects.filter(
                        value__range=(min_value, max_value), month__in=month, indicator_period=p._id)
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
            return Response(content) """

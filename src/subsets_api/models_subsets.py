from mongoengine import *

class Crop(Document):
    #_id = StringField(required=True)
    name = StringField(required=True)
    meta = {'collection': 'indicators_crop'}

class Accession(Document):    
    _id = StringField(required=True)
    name = StringField(required=True)
    number = StringField(required=True)
    acq_date = StringField(required=True)
    aegis =StringField(required=True)
    available = StringField(required=True)
    coll_date = StringField(required=True)
    country_code = StringField(required=True)
    country_name = StringField(required=True)
    country_region_name = StringField(required=True)
    samp_stat = StringField(required=True)
    crop = ReferenceField(Crop)
    doi = StringField(required=True)
    historic = StringField(required=True)
    id = StringField(required=True)
    institute_fullname = StringField(required=True)
    institute_acronym = StringField(required=True)
    geo_lon = FloatField(required=False)
    geo_lat = FloatField(required=False)
    geo_ele = StringField(required=True)
    cellid = IntField()
    taxonomy_genus = StringField(required=True)
    taxonomy_sp_author = StringField(required=True)
    taxonomy_species = StringField(required=True)
    taxonomy_taxon_name = StringField(required=True)
    taxonomy_subtaxa = StringField(required=True)
    taxonomy_subt_author = StringField(required=True)
    coord_flag = StringField(required=True)

    meta = {'collection': 'accession',
            'auto_create_index':False,    
            "index_background": True,
            'indexes': [
        #    {'fields': ['+crop'],},
            ('+crop', '+country_name'),
            ('+crop'),
        ]}

class Indicator(Document):
    _id = StringField(required=True)
    name = StringField(required=True)
    pref = StringField(required=True)
    crop = ReferenceField(Crop)
    indicator_type = StringField(required=True)

    meta = {'collection': 'indicators_indicator'}

class IndicatorPeriod(Document):
    #_id = StringField(required=True)
    period = StringField(required=True)
    indicator = ReferenceField(Indicator)

    meta = {'collection': 'indicators_indicatorperiod'}

class IndicatorValue(Document):
    #_id = StringField(required=True)
    cellid = IntField(required=True)
    indicator_period = ReferenceField(IndicatorPeriod)
    month1 = FloatField(required=False)
    month2 = FloatField(required=False)
    month3 = FloatField(required=False)
    month4 = FloatField(required=False)
    month5 = FloatField(required=False)
    month6 = FloatField(required=False)
    month7 = FloatField(required=False)
    month8 = FloatField(required=False)
    month9 = FloatField(required=False)
    month10 = FloatField(required=False)
    month11 = FloatField(required=False)
    month12 = FloatField(required=False)

    meta = {'collection': 'test',
            'auto_create_index':False,    
            "index_background": True,
            'indexes': [
        #    {'fields': ['+crop'],},
            ('+indicator_period', '+month1','+month2','+month3', 'cellid'),
            ('+indicator_period', '+month4','+month5','+month6', 'cellid'),
            ('+indicator_period', '+month7','+month8','+month9', 'cellid'),
            ('+indicator_period', '+month10','+month11','+month12', 'cellid'),
            ('+indicator_period', '+month1', '+month2', '+month3', '+month4',
             '+month5', '+month6', '+month7', '+month8', '+month9', '+month10',
             '+month11','+month12', 'cellid'),
            ]
            }
    # meta = {'collection': 'indicators_indicatorvalue'}
    

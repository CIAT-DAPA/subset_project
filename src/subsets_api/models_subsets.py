from mongoengine import *
from mongoengine.fields import StringField

class Crop(Document):
    #_id = StringField(required=True)
    name = StringField(required=True)
    meta = {'collection': 'crop'}

class IndicatorType(Document):
    _id = StringField(required=True)
    name = StringField(required=True)

    meta = {'collection': 'indicators_indicatortype'}

class Category(Document):
    _id = StringField(required=True)
    name = StringField(required=True)

    meta = {'collection': 'categories'}

class Indicator(Document):
    _id = StringField(required=True)
    name = StringField(required=True)
    pref = StringField(required=True)
    crop = ReferenceField(Crop)
    indicator_type = ReferenceField(IndicatorType)
    category = ReferenceField(Category)
    unit = StringField(required=True)

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
    value = FloatField(required=False)    
    value_c = IntField(required=False)    

    meta = {'collection': 'indicator_value_v3',
            'auto_create_index':False,    
            "index_background": True,
            'indexes': [
            ('+indicator_period','cellid'),
            ]
            }
    

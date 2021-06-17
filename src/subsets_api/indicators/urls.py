from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import *


#Initialization of router
router = DefaultRouter()
router.register(r'api/indicator', IndicatorPostViewSet, basename='indicators')
router.register(r'api/ind-value', IndicatorValViewSet, basename='indicators')
router.register(r'api/indicators/get', IndicatorViewSet, basename='indicators')
router.register(r'api/accessions', AccessionsList, basename='indicators')
router.register(r'api/crops', CropList, basename='indicators')
#router.register(r'api/accessions/(?P<id>.+)/get', AccessionByIdViewSet, basename='indicators')
urlpatterns = [
    path('', include(router.urls))
]
from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import *


#Initialization of router
router = DefaultRouter()
router.register(r'api/v1/indicator', IndicatorPostViewSet, basename='indicators')
router.register(r'api/v1/ind-value', IndicatorValViewSet, basename='indicators')
router.register(r'api/v1/indicators/get', IndicatorViewSet, basename='indicators')
#router.register(r'api/accessions', AccessionsList, basename='indicators')
router.register(r'api/v1/accessions', AccessionsView, basename='indicators')
router.register(r'api/v1/crops', CropList, basename='indicators')
#router.register(r'api/accessions/(?P<id>.+)/get', AccessionByIdViewSet, basename='indicators')
urlpatterns = [
    path('', include(router.urls))
]
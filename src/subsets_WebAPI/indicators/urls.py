from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import *


#Initialization of router
router = DefaultRouter()
router.register(r'api/accessions', AccesionsViewSet, basename='indicators')
router.register(r'api/accessions/(?P<id>.+)/get', AccesionsByIdViewSet, basename='indicators')
router.register(r'api/accession/biological-status/(?P<name>.+)/get', AccesionsByBiologicalStatusViewSet, basename='indicators')
router.register(r'api/accession/coordinates/(?P<lon>.+)/(?P<lat>.+)/get', AccesionsByCoordinatesViewSet, basename='indicators')
router.register(r'api/crops', CropsViewSet, basename='indicators')
urlpatterns = [
    path('', include(router.urls))
]
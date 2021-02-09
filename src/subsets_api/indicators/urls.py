from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import *


#Initialization of router
router = DefaultRouter()
urlpatterns = [
    path('', include(router.urls))
]
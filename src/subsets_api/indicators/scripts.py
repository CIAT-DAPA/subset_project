from .models import *


def getAccessionsById(id_list):
    response_list = []
    if id_list:
        accessions = Accession.objects.filter(id__in=id_list)
        return accessions
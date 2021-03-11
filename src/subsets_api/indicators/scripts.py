from .models import *


def getAccessionsById(id_list):
    response_list = []
    if id_list:
        for value in id_list:
            accessions = Accession.objects.filter(id=value)
            response_list.append(accessions)
        return response_list
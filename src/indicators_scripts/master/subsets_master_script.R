library(mongolite)
library(jsonlite)
library(RJSONIO)
library(RCurl)

# Passport indicators file
source("../passport/get_passport_data.R")
# Generic indicators file
source("../generic/p95_generic.R")

# Auth with Genesys API
login_genesys()

#connect to Mongo database (accession collection)
passport_indicators<-mongo(collection = 'indicators_accession', db = 'indicator')

#connect to Mongo database (indicators values collection)
mng_conn_indicatorValue<-mongo(collection = 'indicators_indicatorvalue', db = 'indicator')

#Inserting indicators values
mng_conn_indicatorValue$insert(data)

#' Get accession passport data by crop
#' @param crop a vector of crop names
accession_data<-get_passport_data("cassava")

#inserting json data extracted before  
mng_conn$insert(jsonlite::fromJSON(accession_data))



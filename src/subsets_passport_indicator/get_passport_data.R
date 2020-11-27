#' Get the authorization code to login to Genesys
#'

login_genesys <- function(){
  #setup production environment
  genesysr::setup_production()
  
  #login to get the authorization code
  genesysr::user_login()
}


#' Get accession passport data by crop
#' @param crop a vector of crop names
#'
#' @return JSON data

get_passport_data <- function(crop){
  
  #fields to get from Genesys
  fields <- c("accessionName",
              "accessionNumber",
              "acquisitionDate",
              "id",
              "aegis",
              "available",
              "coll.collDate",
              "coll.collSite",
              "countryOfOrigin.code3",
              "countryOfOrigin.name",
              "countryOfOrigin.region.name",
              "crop.name",
              "doi",
              "donorCode",
              "donorName",
              "geo.elevation",
              "geo.latitude",
              "geo.longitude",
              "geo.tileIndex",
              "historic",
              "institute.acronym",
              "institute.code",
              "institute.fullName",
              "sampStat",
              "mlsStatus", 
              "storage1",
              "storage2",
              "storage3",
              "storage4",
              "taxonomy.genus",
              "taxonomy.spAuthor",
              "taxonomy.species",
              "taxonomy.subtAuthor",
              "taxonomy.subtaxa",
              "taxonomy.taxonName"
  )
  
  #get passport data
  accessions <- genesysr::get_accessions(list(crop = crop), fields = fields)
  
  #convert to JSON
  accessions_json <- jsonlite::toJSON(accessions)
  
  accessions_json
  
}
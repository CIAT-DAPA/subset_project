library(futile.logger)

# Setting logging logger and appender
flog.threshold(INFO, name = 'passport')

# Writing log messages in console and file
flog.appender(appender.tee('passport_data.log'), name = 'passport')

#'Log Info
#'

log_info <- function(message, ...){
  futile.logger::flog.info(message, name = 'passport', ...)
}

#' Log warnings
#'
#'

log_warning <- function(message){
  futile.logger::flog.warn(message, name = 'passport')
}

#' Log errors
#'
#'

log_error <- function(message){
  futile.logger::flog.error(message, name = 'passport')
}

#' Get the authorization code to login to Genesys
#'

login_genesys <- function(){
  #setup production environment
  genesysr::setup_production()
  
  #login to get the authorization code
  log_info(message = "Authorizing to Genesys")
  genesysr::user_login()
}


#' Get accession passport data by crop
#' @param crop a vector of crop names
#'
#' @return dataframe

get_passport_data <- function(crop){
  
  require(dplyr)
  
  #fields to get from Genesys
  fields <- c("accessionName",
              "accessionNumber",
              "available",
              "coll.collDate",
              "countryOfOrigin.code3",
              "countryOfOrigin.name",
              "countryOfOrigin.region.name",
              "crop.name",
              "doi",
              "geo.elevation",
              "geo.latitude",
              "geo.longitude",
              "id",
              "institute.acronym",
              "institute.code",
              "institute.fullName",
              "mlsStatus",
              "sampStat",
              "taxonomy.genus",
              "taxonomy.spAuthor",
              "taxonomy.species",
              "taxonomy.subtAuthor",
              "taxonomy.subtaxa",
              "taxonomy.taxonName"
  )
  
  #standardize names
  std_names <- c("accession_name",
                 "accession_number",
                 "available",
                 "coll_date",
                 "country_of_origin_code3",
                 "country_of_origin_name",
                 "country_of_origin_region_name",
                 "crop_name",
                 "doi",
                 "elevation",
                 "latitude",
                 "longitude",
                 "id",
                 "institute_acronym",
                 "institute_code",
                 "institute_full_name",
                 "mls_status",
                 "samp_stat",
                 "taxonomy_genus",
                 "taxonomy_sp_author",
                 "taxonomy_species",
                 "taxonomy_subt_author",
                 "taxonomy_subtaxa",
                 "taxonomy_taxon_name"
  )
  
  tryCatch({
    
    #get passport data
    log_info(message = "Getting accessions passport data for crop(s): %s", crop)
    
    accessions <- genesysr::get_accessions(list(crop = crop), fields = fields)
    
    if(nrow(accessions) == 0){
      err <- simpleError("No records extracted. Please check the validity of crop(s) name(s) passed as argument!")
      stop(err)
    }
    
    else log_info("%s accessions are extracted.", nrow(accessions))
  
    #keep just columns included in fields
    accessions <- accessions %>% dplyr::select(any_of(fields))
  
    #modify accessions column names
    for (i in 1:length(fields)) { 
      colnames(accessions)[which(names(accessions) == fields[i])] <- std_names[i]
    }
  },
  
  custom_error = function(e) {
    err <- conditionMessage(e)
    log_error(err)
  },
  
  error = function(error) {
    log_error(error)
    stop(error)
  },
  
  warning = function(warning) {
    log_warning(warning)
    stop()
  })
  
  accessions
  
}
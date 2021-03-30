#' Get the authorization code to login to Genesys
#'

login_genesys <- function(){
  #setup production environment
  genesysr::setup_production()
  
  genesysr::user_login()
}


#' Get accession passport data by crop
#' @param crop a vector of crop names
#'
#' @return dataframe

get_passport_data <- function(crop){
  
  library(futile.logger)
  library(dplyr)
  library(raster)
  library(here)
  
  #the working directory should be any folder inside the project folder
  root_folder = here()
  
  source(file = paste0(root_folder, "/src/indicators_scripts/tools/logging.R"), local = TRUE)
  
  # set up the logging context
  set_logger_appender('passport', 'passport.log')
  
  #fields to get from Genesys
  fields <- c("accessionName",
              "accessionNumber",
              "acquisitionDate",
              "aegis",
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
              "historic",
              "id",
              "institute.acronym",
              "institute.fullName",
              "sampStat",
              "taxonomy.genus",
              "taxonomy.spAuthor",
              "taxonomy.species",
              "taxonomy.subtAuthor",
              "taxonomy.subtaxa",
              "taxonomy.taxonName"
  )
  
  #standardize names
  std_names <- c("name",
                 "number",
                 "acq_date",
                 "aegis",
                 "available",
                 "coll_date",
                 "country_code",
                 "country_name",
                 "country_region_name",
                 "crop_name",
                 "doi",
                 "geo_ele",
                 "geo_lat",
                 "geo_lon",
                 "historic",
                 "id",
                 "institute_acronym",
                 "institute_fullname",
                 "samp_stat",
                 "taxonomy_genus",
                 "taxonomy_sp_author",
                 "taxonomy_species",
                 "taxonomy_subt_author",
                 "taxonomy_subtaxa",
                 "taxonomy_taxon_name"
  )
  
  tryCatch(
    
    withCallingHandlers({
      #get passport data
      log_info('passport', message = "Getting accessions passport data for crop(s): %s", crop)
    
      accessions <- genesysr::get_accessions(list(crop = crop), fields = fields)
    
      if(nrow(accessions) == 0){
        err <- simpleError("No records extracted. Please check the validity of crop(s) name(s) passed as argument!")
        stop(err)
      }
    
      else log_info('passport', "%s accessions are extracted.", nrow(accessions))
  
      #keep just columns included in fields
      accessions <- accessions %>% dplyr::select(any_of(fields))
  
      #modify accessions column names
      for (i in 1:length(fields)) { 
        colnames(accessions)[which(names(accessions) == fields[i])] <- std_names[i]
      }
    
      #get raster base file
      tmp_directory = tempdir()
      unzip(paste0(root_folder, "/data/builder_indicators/raster_base_complete.zip"), exdir = tmp_directory)
      base <- raster(file.path(tmp_directory,"raster_base_complete.asc"))
    
      #get cellID from coordinates
      cellid <- cellFromXY(base, accessions[,c("geo_lon","geo_lat")])
      accessions <- cbind(cellid, accessions)
     
    },
    warning = function(w) {
      log_warning('passport', w$message)
    }
  ),
  
  custom_error = function(e) {
    err <- conditionMessage(e)
    log_error(err)
  },
  
  error = function(error) {
    log_error('passport', error)
    stop(error)
  })
  
  accessions
  
}
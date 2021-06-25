#' Get the authorization code to login to Genesys
#'

login_genesys <- function(){
  #setup production environment
  genesysr::setup_production()
  
  genesysr::user_login()
}

#' Flag longitude/latitude coordinates to indicate their validity or invalidity. There are four flags:
#' "NA": for NA coordinates
#' "invalid": for lat > 90, lat < -90, lon > 180 and lon < -180
#' "point in sea": for coordinates outside the land. The shapefile used is downloaded from \url{https://osmdata.openstreetmap.de/download/land-polygons-complete-4326.zip}.
#' "valid": for good coordinates values
#'
#' @param data dataframe containing coordinates data
#' @param lon character: longitude column name
#' @param lat character: latitude column name
#'
#' @return the same input dataframe with additional column "coord_flag". 
#' 
#' @importFrom CoordinateCleaner cc_val cc_sea
#' @importFrom dplyr filter
#' @importFrom rgdal readOGR

flag_coordinates <- function(data, lon = "geo_lon", lat = "geo_lat"){
  
  #flag records with na coordinates
  na <- list(
    is.na(data[[lon]]), 
    is.na(data[[lat]])
  )
  na <- Reduce("|", na)
  data.na <- data[na,]
  coord_flag <- "NA"
  if(nrow(data.na)){
    data.na.flagged <- cbind(coord_flag, data.na)
    flagged.data <- data.na.flagged
  }
  
  #flag invalid coordinates values
  data <- data[!na,]
  wrong.val <- CoordinateCleaner::cc_val(data, lon, lat, value = "flagged")
  data.wrong.val <- data[!wrong.val,]
  
  coord_flag <- "invalid"
  if(nrow(data.wrong.val)){
    data.val.flagged <- cbind(coord_flag, data.wrong.val)
    flagged.data <- rbind(flagged.data, data.val.flagged)
  }
  
  #get cleaned data from invalid coordinates
  data.cleaned.val <- data[wrong.val,]
  cleaned.data <- data.cleaned.val
  if(nrow(data.cleaned.val)){
    
    #read the land polygons shapefile located in the data folder
    ref <- rgdal::readOGR("../../../data/builder_indicators/land-polygons-complete-4326/land_polygons.shp")
    
    #get sea flagged records
    value.sea <- CoordinateCleaner::cc_sea(data.cleaned.val, lon, lat, value = "flagged", ref = ref)
    data.sea <- data[!value.sea,]
    
    if(nrow(data.sea)){
      coord_flag <- "point in sea"
      data.sea.flagged <- cbind(coord_flag, data.sea)
      
      #filter from sea flagged data records that are flagged as invalid before combining data.sea.flagged and flagged.data
      data.sea.flagged <- dplyr::filter(data.sea.flagged, !id %in% intersect(data.sea.flagged$id, flagged.data$id))
      flagged.data <- rbind(data.sea.flagged, flagged.data)
    }
    
    #get cleaned data from coordinates in sea
    data.cleaned.sea <- data.cleaned.val[value.sea,]
    
    coord_flag <- "valid"
    cleaned.data <- cbind(coord_flag, data.cleaned.sea)
  }
  
  data.combined <- rbind(cleaned.data, flagged.data)
  
  return(data.combined)
  
}

#'convert coordinates to country using rworldmap package
#'need to install rworldmap and rworldxtra
#'

coords2country <- function(points)
{  
  countriesSP <- rworldmap::getMap(resolution='high')
  
  pointsSP = sp::SpatialPoints(points, proj4string=CRS(proj4string(countriesSP)))  
  
  indices = sp::over(pointsSP, countriesSP)
  
  # get country name
  country <- indices$ADMIN
  
  return(country)
}


#' Get accession passport data by crop
#' @param crop a vector of crop names
#'
#' @return dataframe

get_passport_data <- function(crop){
  
  library(futile.logger)
  library(dplyr)
  library(raster)
  
  
  source(file = "../../../src/indicators_scripts/tools/logging.R", local = TRUE)
  
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
              "cropName",
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
  
  tryCatch({
    options(warning.expression=quote(function(){}))
    withCallingHandlers({
      #get passport data
      log_info('passport', message = "Getting accessions passport data for crop(s): %s", crop)
    
      accessions <- genesysr::get_accessions(list(crop = crop), fields = fields)
    
      if(nrow(accessions) == 0){
        err <- simpleError("No records extracted. Please check the validity of crop(s) name(s) passed as argument!")
        stop(err)
      }
    
      else log_info('passport', "%s accessions are extracted.", nrow(accessions))
      
      # add longitude and latitude columns if not existing
      coord <- c("geo.latitude", "geo.longitude")
      accessions[coord[!(coord %in% names(accessions))]] <- NA
      
      #keep just columns included in fields
      accessions <- accessions %>% dplyr::select(any_of(fields))
  
      #modify accessions column names
      for (i in 1:length(fields)) { 
        colnames(accessions)[which(names(accessions) == fields[i])] <- std_names[i]
      }
      
      #add country names based on coordinates
      acc.with.rowname <- accessions %>% add_rownames
      accessions = acc.with.rowname %>% filter(!is.na(geo_lon) & !is.na(geo_lat)) %>%
        mutate(country_name = ((.) %>% select(geo_lon, geo_lat)) %>% coords2country()) %>%
        bind_rows(., anti_join(acc.with.rowname, ., by = "rowname"))%>% arrange(as.numeric(rowname))
      accessions <- as.data.frame(accessions[,-1])
      
      #get raster base file
      tmp_directory = tempdir()
      unzip("../../../data/builder_indicators/raster_base_complete.zip", exdir = tmp_directory)
      base <- raster(file.path(tmp_directory,"raster_base_complete.asc"))
    
      #get cellID from coordinates
      cellid <- cellFromXY(base, accessions[,c("geo_lon","geo_lat")])
      accessions <- cbind(cellid, accessions)
      
      #flag coordinates of accessions
      accessions <- flag_coordinates(accessions)
     
    },
    warning = function(w) {
      log_warning('passport', w$message)
    }
  )},
  
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
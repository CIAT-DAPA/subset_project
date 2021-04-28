#' Flag longitude/latitude coordinates to indicate their validity or invalidity. There are four flags:
#' "NA": for NA coordinates
#' "invalid": for lat > 90, lat < -90, lon > 180 and lon < -180
#' "point in sea": for coordinates outside the land. The shapefile used is downloaded from \url{https://osmdata.openstreetmap.de/data/land-polygons.html}.
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
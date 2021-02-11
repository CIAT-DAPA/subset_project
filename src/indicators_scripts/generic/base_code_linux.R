### Base Code Linux
## Brayan Mora 
# Code for run code ind_generic


options(warn = -1); options(scipen = 999); g <- gc(reset = T); rm(list = ls())
ruta <- "/mnt/workspace_cluster_2/SubsettingTool/codes/"
source(paste0(ruta,"ind_generic.R"))


#### Precipitation indicators
year <- 1983:2016
lapply(1:length(year), function(i){
  cat(paste0("Processing year:::--> ",i," of " ,length(year), "\n"))
  root   <- "/mnt/workspace_cluster_2/SubsettingTool/" 
  base   <- raster(paste0(root,"Inputs/raster_base.asc"))
  input  <- "/mnt/workspace_cluster_13/GATES/rds/chirps/"
  output <- paste0(root,"output/")
  
  ind_precipitation(root=root ,base=base ,continent="Europe",
                    input =input ,output =output, year=year[i],coress= 20,type = "ind_prec")
})


####  Temperature Indicators 
year <- 1983:2016
lapply(1:length(year), function(i){
  cat(paste0("Processing year:::--> ",i," of " ,length(year), "\n"))
  root <- "/mnt/workspace_cluster_2/SubsettingTool/" 
  base <- raster(paste0(root,"Inputs/raster_base.asc"))
  input  <- "/mnt/workspace_cluster_13/GATES/rds/chirts/"
  output <- paste0(root,"output/")
  
  ind_temp(root=root ,base=base ,continent="Europe",
           input =input ,output =output, year=year[i],coress= 20,type = "ind_prec")
})


####  Index daylength 
year <- 1983:2016
lapply(1:length(year), function(i){
  cat(paste0("Processing year:::--> ",i," of " ,length(year), "\n"))
  root <- "/mnt/workspace_cluster_2/SubsettingTool/" 
  base <- raster(paste0(root,"Inputs/raster_base.asc"))
  input  <- "/mnt/workspace_cluster_13/GATES/rds/chirps/"
  output <- paste0(root,"output/")
  
  long_day(root=root ,base=base ,continent="Europe",
           input =input ,output =output, year=year[i],coress= 20,type = "ind_time")
})



#### Indicators VPD

year <- 1983:2016
lapply(1:length(year), function(i){
  cat(paste0("Processing year:::--> ",i," of " ,length(year), "\n"))
  root <- "/mnt/workspace_cluster_2/SubsettingTool/" 
  base <- raster(paste0(root,"Inputs/raster_base.asc"))
  input  <- "/mnt/workspace_cluster_13/GATES/rds/chirts/"
  output <- paste0(root,"output/")
  
  vpd(root=root ,base=base ,continent="Europe",
      input =input ,output =output, year=year[i],coress= 20,type = "ind_vpd")
})


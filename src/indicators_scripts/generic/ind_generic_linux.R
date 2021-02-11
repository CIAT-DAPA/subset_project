#### Generic Indicators Calc Linux
## Brayan Mora
## Create functions for calculate generic indicators 
###################################################################################################
###################################  Index Precipitation ##########################################
###################################################################################################
options(warn = -1); options(scipen = 999); g <- gc(reset = T); rm(list = ls())
require(pacman)
pacman::p_load(raster, rgdal, doSNOW, foreach, parallel, magrittr, rgeos, gtools, stringr, sf, glue, tidyverse,gtools)

ind_precipitation <- function(root, base, continent, input, output,year,type,coress){
  clima <- readRDS(paste0(input,continent,"_chirps_",year,".rds"))
  clima <- as.data.frame(clima)
  cellID <- cellFromXY(base, clima[,1:2])
  clima <- cbind(cellID, clima)
  
  prec <- clima
  names <- colnames(prec[,-(1:3)])
  nms <- gsub("y_", "", names)
  nms <- gsub('\\_', '-', nms)
  nms <- c("cellID","lon","lat", nms)
  colnames(prec) <- nms
  
  library(doSNOW);library(foreach);library(parallel);library(doParallel)
  ind_prec_cal<- mclapply(1:nrow(prec), function(i){
    cat(paste0("pixel number:: ",i, "_of_", nrow(prec),"\n" ))
    require(dplyr)
    time.serie <- prec[i, 1:ncol(prec)]
    
    suppressMessages(library(tidyverse))
    suppressMessages(library(compiler))
    
    X <- time.serie
    X <- X %>% gather(key = Date, value = Value, -(cellID:lat))
    X$Year <- lubridate::year(as.Date(X$Date))
    X$Month <- lubridate::month(as.Date(X$Date))
    
    # 1.Percentil 95 prec  
    p_95<- X %>% dplyr::group_by(Month) %>% dplyr::arrange(Date)%>% summarise(P_95 = quantile(Value, probs = .95, na.rm = TRUE))
    p_95 <- p_95 %>% as.data.frame
    names(p_95)[2] <- "Value"; p_95$Variable <- "p_95"
    Year <- unique(X$Year)
    p_95 <- cbind(Year,p_95) 
    
    # 2. Total_ rain
    t_rain <- X %>% dplyr::group_by(Month) %>% dplyr::arrange(Date)%>% summarise(t_rain = sum(Value, na.rm = TRUE))
    t_rain <- t_rain %>% as.data.frame
    names(t_rain)[2] <- "Value"; t_rain$Variable <- "t_rain"
    Year <- unique(X$Year)
    t_rain <- cbind(Year,t_rain) 
    
    
    #3. Consecutive dry days
    
    dr_stress <- function(PREC, p_thresh = 1){
      runs <- rle(PREC < p_thresh)
      cons_days <- max(runs$lengths[runs$values==1], na.rm=TRUE)
      return(cons_days)
    }
    dr_stressCMP <- cmpfun(dr_stress); rm(dr_stress)
    cdd <- X %>% dplyr::group_by(Month) %>% dplyr::arrange(Date)%>% summarise(CDD = dr_stressCMP(Value, p_thresh = 1))
    cdd <- cdd %>% as.data.frame
    names(cdd)[2] <- "Value"; cdd$Variable <- "CDD"
    Year <- unique(X$Year)
    cdd <- cbind(Year,cdd) 
    
    results<- data.frame(cellID= unique(X$cellID), rbind(p_95,t_rain,cdd))
    return(results)
  }, mc.cores = 20, mc.preschedule = F)
  
  tabla <- do.call(rbind, ind_prec_cal)
  saveRDS(tabla, paste0(output,type,"/",type,"_",continent,"_",year,".rds"))
  cat(">>> Results saved successfully ...\n")
}

###################################################################################################
###################################  Index temperature ############################################
###################################################################################################

ind_temp <- function(root, base, continent, input, output,year,type, coress){
  
  tmax <- readRDS(paste0(input,"Tmax_",continent,"_chirts_",year,".rds"))
  tmin <- readRDS(paste0(input,"Tmin_",continent,"_chirts_",year,".rds"))
  
  cellID <- cellFromXY(base, tmax[,1:2])
  tmax <- cbind(cellID,tmax)
  
  cellID <- cellFromXY(base, tmin[,1:2])
  tmin <- cbind(cellID,tmin)
  
  names <- colnames(tmax[,-(1:3)])
  nms <- gsub("y_", "", names)
  nms <- gsub('\\_', '-', nms)
  nms <- c("cellID","lon","lat", nms)
  colnames(tmax) <- nms
  colnames(tmin) <- nms
  
  if(ncol(tmin) == 368){
    tmin <- tmin}else{
      tmin <- tmin[,-63] 
    }
  if(ncol(tmax) == 368){
    tmax <- tmax}else{
      tmax <- tmax[,-63]
    }
  #Proceso en paralelo 
  library(doSNOW);library(foreach);library(parallel);library(doParallel)
  index_temp <- mclapply(1:nrow(tmin), function(i){  
    cat(paste0("pixel number:: ",i, "_of_", nrow(tmin),"\n" ))
    require(dplyr)
    time.serie   <- tmax[i, 1:ncol(tmax)]
    time.serie.1 <- tmin[i, 1:ncol(tmin)]
    
    suppressMessages(library(tidyverse))
    suppressMessages(library(compiler))
    
    X <- time.serie
    X <- X %>% gather(key = Date, value = Value, -(cellID:lat))
    X$Year <- lubridate::year(as.Date(X$Date))
    X$Month <- lubridate::month(as.Date(X$Date))
    
    
    Y <- time.serie.1
    Y <- Y %>% gather(key = Date, value = Value, -(cellID:lat))
    Y$Year <- lubridate::year(as.Date(Y$Date))
    Y$Month <- lubridate::month(as.Date(Y$Date))
    
    
    # 1.  MEDIA DE TEMPERATURA MAXIMA  
    TX <- X %>% dplyr::group_by(Month) %>% dplyr::arrange(Date)%>% summarise(mean_tmax = mean(Value))
    TX <- TX %>% as.data.frame
    names(TX)[2] <- "Value"; TX$Variable <- "TX" 
    Year <- unique(X$Year)
    TX <- cbind(Year,TX) 
    
    
    # 2.  MEDIA DE TEMPERATURA MINIMA  
    TN<- Y %>% dplyr::group_by(Month) %>% dplyr::arrange(Date)%>% summarise(mean_tmin = mean(Value))
    TN <- TN %>% as.data.frame
    names(TN)[2] <- "Value"; TN$Variable <- "TN"
    Year <- unique(X$Year)
    TN <- cbind(Year,TN) 
    
    results<- data.frame(cellID= unique(X$cellID), rbind(TX,TN))
    return(results)
    
  }, mc.cores = 20, mc.preschedule = F)
  tabla <- do.call(rbind, index_temp)
  saveRDS(tabla, paste0(output,type,"/",type,"_",continent,"_",year,".rds"))
  cat(">>> Results saved successfully ...\n")
}


###################################################################################################
###################################    Index daylength    #########################################
###################################################################################################

long_day <- function(root, year,input,continent,output,type,coress,base){
  df <- readRDS(paste0(input,continent,"_chirps_1983.rds"))
  cor <- df[,1:2]
  colnames(cor)<- c("lon","lat")
  cellID <- cellFromXY(base, cor)
  cor <- cbind(cellID,cor)
  rm(df)
  date <- seq(as.Date(paste0(year,"/1/1")), by = "month", length.out = 12)
  #Proceso en paralelo 
  library(doSNOW);library(foreach);library(parallel);library(doParallel)
  
  long <- mclapply(1:nrow(cor), function(i) { 
    cat(paste0("pixel number:: ",i, "_of_", nrow(cor),"\n" ))
    
    require(geosphere)
    require(dplyr)
    dl <- as.data.frame(t(daylength(cor$lat[i], date)))
    df <- cbind(cor$cellID[i], dl)
    colnames(df) <- c("cellID", as.character(as.Date(date)))
    return(df)
  }, mc.cores = 20, mc.preschedule = F))
tabla <- do.call(rbind, long)
saveRDS(tabla, paste0(output,type,"/",type,"_",continent,"_",year,".rds"))  
cat(">>> Results saved successfully ...\n")
}

######################################################################################################
###########################           Indicators VPD         #########################################
######################################################################################################

vpd <- function(year,root,input,output,continent,type,coress){
  tmax <- readRDS(paste0(input,"Tmax_",continent,"_chirts_",year,".rds"))
  tmin <- readRDS(paste0(input,"Tmin_",continent,"_chirts_",year,".rds"))
  
  cellID <- cellFromXY(base, tmax[,1:2])
  tmax <- cbind(cellID,tmax)
  
  cellID <- cellFromXY(base, tmin[,1:2])
  tmin <- cbind(cellID,tmin)
  
  names <- colnames(tmax[,-(1:3)])
  nms <- gsub("y_", "", names)
  nms <- gsub('\\_', '-', nms)
  nms <- c("cellID","lon","lat", nms)
  colnames(tmax) <- nms
  colnames(tmin) <- nms
  
  if(ncol(tmin) == 368){
    tmin <- tmin}else{
      tmin <- tmin[,-63] 
    }
  if(ncol(tmax) == 368){
    tmax <- tmax}else{
      tmax <- tmax[,-63]
    }
  
  #Proceso en paralelo 
  library(doSNOW);library(foreach);library(parallel);library(doParallel)
  system.time(calc_vpd <- mclapply(1:nrow(tmin), function(i){ 
    require(dplyr)
    time.serie <- tmax[i, 1:ncol(tmax)]
    time.serie.1 <- tmin[i, 1:ncol(tmin)]
    
    suppressMessages(library(tidyverse))
    suppressMessages(library(compiler))
    
    X <- time.serie
    X <- X %>% gather(key = Date, value = Value, -(cellID:lat))
    X$Year <- lubridate::year(as.Date(X$Date))
    X$Month <- lubridate::month(as.Date(X$Date))
    
    
    Y <- time.serie.1
    Y <- Y %>% gather(key = Date, value = Value, -(cellID:lat))
    Y$Year <- lubridate::year(as.Date(Y$Date))
    Y$Month <- lubridate::month(as.Date(Y$Date))
    
    #Vapour pressure deficit
    calc_vpd <- function(tmin, tmax){
      
      #constants
      albedo <- 0.2
      vpd_cte <- 0.7
      
      #soil heat flux parameters
      a_eslope=611.2
      b_eslope=17.67
      c_eslope=243.5
      
      #input parameters
      tmean <- (tmin+tmax)/2
      
      #soil heat flux
      eslope=a_eslope*b_eslope*c_eslope/(tmean+c_eslope)^2*exp(b_eslope*tmean/(tmean+c_eslope))
      
      #estimate vpd
      esat_min=0.61120*exp((17.67*tmin)/(tmin+243.5))
      esat_max=0.61120*exp((17.67*tmax)/(tmax+243.5))
      vpd=vpd_cte*(esat_max-esat_min) #kPa
      return(vpd)
    }
    
    vpd <- as.data.frame(calc_vpd(tmin = Y$Value, tmax = X$Value ))
    vpd <- data.frame(cellID = X$cellID, lon= X$lon, lat= X$lat, Value= vpd,Year= X$Year,Date=X$Date) 
    names(vpd)<- c("cellID","lon","lat","Value","Year","Date")
    vpd$Month <- X$Month
    
    VPD <- vpd %>% dplyr::group_by(Month)%>% summarise(VPD = mean(Value))
    VPD <- VPD %>% as.data.frame
    names(VPD)[2] <- "Value"; VPD$Variable <- "VPD" 
    Year <- unique(X$Year)
    VPD <- cbind(Year,VPD)
    
    NVPD4 <- vpd %>% dplyr::group_by(Month) %>% summarise(NVPD4 = sum(Value >= 4))
    NVPD4 <- NVPD4 %>% as.data.frame
    names(NVPD4)[2] <- "Value"; NVPD4$Variable <- "NVPD4"
    Year <- unique(X$Year)
    NVPD4 <- cbind(Year,NVPD4) 
    
    results <- data.frame(cellID= unique(X$cellID), rbind(VPD,NVPD4))
    return(results)
  }, mc.cores = 20, mc.preschedule = F))
  tabla <- do.call(rbind, calc_vpd)
  saveRDS(tabla, paste0(output,type,"/",type,"_",continent,"_",year,".rds")) 
  cat(">>> Results saved successfully ...\n")
}





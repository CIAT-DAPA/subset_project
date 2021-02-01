#####Test Para Africa 
g=gc()
rm(list=ls())
require(raster)
root <- "//dapadfs/workspace_cluster_9/CWR_pre-breeding/"

year <- 1983
ind <- function(year, continent){
  base <- raster("//dapadfs/workspace_cluster_13/GATES/raster/indicators/dryDays/monthly/dry_days_1981_1.asc")
  clima <- readRDS(paste0("//dapadfs/workspace_cluster_13/GATES/rds/chirps/",continent,"_chirps_",year,".rds"))
  clima <- as.data.frame(clima)
  cellID <- cellFromXY(base, clima[,1:2])
  clima <- cbind(cellID, clima)
  
  prec <- clima
  names <- colnames(prec[,-(1:3)])
  nms <- gsub("y_", "", names)
  nms <- gsub('\\_', '-', nms)
  nms <- c("cellID","lon","lat", nms)
  colnames(prec) <- nms
  
  ###############################
  # Calculo de indicadores Prec #
  ###############################
  #Proceso en paralelo 
  library(doSNOW);library(foreach);library(parallel);library(doParallel)
  cores<- detectCores()
  cl<- makeCluster(cores-10)
  registerDoParallel(cl)
  
  system.time(indexes_cassava <- foreach(i=1:nrow(prec), .verbose = TRUE) %dopar% {  
    require(dplyr)
    mylist <- list()
    time.serie <- prec[i, 1:ncol(prec)]
    
    require(dplyr)
    require(tidyr)
    suppressMessages(library(compiler))
    
    X <- time.serie
    X <- X %>% gather(key = Date, value = Value, -(cellID:lat))
    X$Year <- lubridate::year(as.Date(X$Date))
    X$Month <- lubridate::month(as.Date(X$Date))
    
    # 1.  Percentil 95 prec  
    p_95<- X %>% dplyr::group_by(Month) %>% dplyr::arrange(Date)%>% summarise(P_95 = quantile(Value, probs = .95, na.rm = TRUE))
    p_95 <- p_95 %>% as.data.frame
    names(p_95)[2] <- "Value"; p_95$Variable <- "p_95"
    Year <- unique(X$Year)
    p_95 <- cbind(Year,p_95) 
    
    results<- data.frame(cellID= unique(X$cellID), p_95)
    mylist[[i]] <- results
    
  })
  stopCluster(cl)
  
  tabla <- do.call(rbind, indexes_cassava)
  tabla$year <- NULL
  
  tabla$Year <- as.numeric(tabla$Year)
  tabla$Value <- as.numeric(tabla$Value)
  tabla$cellID <- as.numeric(tabla$cellID)
  tabla$Month <- as.numeric(tabla$Month)
  
  tabla <- tabla[complete.cases(tabla),]
  tabla <- unique(tabla)
  vars <- c(as.character(unique(tabla$Variable)))
  
  spread_tables <- lapply(1:length(vars), function(i){
    df <- tabla %>% filter(Variable == vars[i])
    df <- df %>% tidyr::spread(Month, Value) # %>% dplyr::group_by(Variable)
    df$Variable <- NULL
    names(df)[2:ncol(df)] <- paste0(vars[i],"-",unique(df$Year), "-", names(df)[2:ncol(df)])
    df[,2] <- NULL
    return(df)
  })
  tabla2 <- Reduce(function(...) merge(..., by = "cellID", all.x= T), spread_tables)
  saveRDS(tabla2, paste0(root,"/subsetting/",continent,"_todo_",year,".rds"))  
  
}

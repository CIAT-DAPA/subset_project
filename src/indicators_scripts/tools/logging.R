#'
#'
#'
set_logger_appender <- function(logger_name, log_filename){
  # Setting logging logger and appender
  flog.threshold(INFO, name = logger_name)
  
  # Writing log messages in console and file
  flog.appender(appender.tee(log_filename), name = logger_name)
}


#'Log Info
#'

log_info <- function(logger_name, message, ...){
  futile.logger::flog.info(message, name = logger_name, ...)
}

#' Log warnings
#'
#'

log_warning <- function(logger_name, message){
  futile.logger::flog.warn(message, name = logger_name)
}

#' Log errors
#'
#'

log_error <- function(logger_name, message){
  futile.logger::flog.error(message, name = logger_name)
}
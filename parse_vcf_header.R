parse_vcf_header <- function(vcf_path) {
  # Initialize empty data frames to hold results
  info_fields <- data.frame(ID=character(), Number=character(), Type=character(), Description=character(), stringsAsFactors=FALSE)
  format_fields <- data.frame(ID=character(), Number=character(), Type=character(), Description=character(), stringsAsFactors=FALSE)
  
  # Regular expressions with capture groups
  info_regex <- '^##INFO=<ID=([^,]+),Number=([^,]+),Type=([^,]+),Description="(.*)"'
  format_regex <- '^##FORMAT=<ID=([^,]+),Number=([^,]+),Type=([^,]+),Description="(.*)"'
  
  # Open the connection (automatically handles .gz or plaintext)
  if (endsWith(vcf_path, ".gz")) {
    con <- gzfile(vcf_path, "rt")
  } else {
    con <- file(vcf_path, "rt")
  }
  
  # Ensure the connection closes safely when the function finishes or errors out
  on.exit(close(con))
  
  # Read line by line
  while (TRUE) {
    line <- readLines(con, n = 1, warn = FALSE)
    
    # Break out of loop if we hit the end of the file or the main data header row
    if (length(line) == 0 || grepl("^#CHROM", line)) {
      break
    }
    
    # Check and parse INFO line
    if (grepl(info_regex, line)) {
      # regmatches extracts the captured groups
      matches <- regmatches(line, regexec(info_regex, line))[[1]]
      # matches[1] is the whole line, matches[2:5] are the capture groups
      info_fields <- rbind(info_fields, data.frame(
        ID = matches[2], Number = matches[3], Type = matches[4], Description = matches[5], 
        stringsAsFactors = FALSE
      ))
    }
    
    # Check and parse FORMAT line
    if (grepl(format_regex, line)) {
      matches <- regmatches(line, regexec(format_regex, line))[[1]]
      format_fields <- rbind(format_fields, data.frame(
        ID = matches[2], Number = matches[3], Type = matches[4], Description = matches[5], 
        stringsAsFactors = FALSE
      ))
    }
  }
  
  # Return both structures as a named list
  return(list(info = info_fields, format = format_fields))
}

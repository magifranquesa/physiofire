# Load the project configuration (config/config.yaml) from R.
# Usage: source("R/config.R"); cfg <- load_config()

find_repo_root <- function(start = getwd()) {
  dir <- normalizePath(start, winslash = "/", mustWork = TRUE)
  repeat {
    if (file.exists(file.path(dir, "config", "config.yaml"))) return(dir)
    parent <- dirname(dir)
    if (parent == dir) stop("Repository root (config/config.yaml) not found from: ", start)
    dir <- parent
  }
}

load_config <- function(path = NULL) {
  root <- find_repo_root()
  if (is.null(path)) path <- file.path(root, "config", "config.yaml")
  cfg <- yaml::read_yaml(path)
  # Resolve paths relative to the repository root
  cfg$paths <- lapply(cfg$paths, function(p) file.path(root, p))
  cfg
}

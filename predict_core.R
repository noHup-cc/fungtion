#' Core R prediction script for fungtion
#' Usage: Rscript predict_core.R --features features.csv --output output.txt

suppressPackageStartupMessages({
  library(e1071)
  library(caret)
  library(optparse)
})

get_script_dir <- function() {
  cmd_args <- commandArgs(trailingOnly = FALSE)
  file_arg <- "--file="
  script_path <- sub(file_arg, "", cmd_args[grep(file_arg, cmd_args)])
  if (length(script_path) == 0) {
    stop("Unable to determine script path")
  }
  dirname(normalizePath(script_path[1]))
}

option_list = list(
  make_option(c("--features"), type="character", help="Input features csv"),
  make_option(c("--output"), type="character", help="Output file for scores")
)
opt = parse_args(OptionParser(option_list=option_list))

features_file = opt$features
output_file = opt$output

# Load features
features = read.csv(features_file, header=TRUE)
features[is.na(features)] <- 0

# Load all SVM models and average predictions
model_dir = file.path(get_script_dir(), 'model')
model_files = list.files(model_dir, pattern='*.rds', full.names=TRUE)
if(length(model_files) == 0) stop('No model files found!')

pred_matrix = matrix(0, nrow=nrow(features), ncol=length(model_files))
for(i in seq_along(model_files)) {
  model = readRDS(model_files[i])
  pred = predict(model, features, probability=TRUE)
  prob = attr(pred, 'probabilities')[,1]
  pred_matrix[,i] = prob
}
# Average over models
final_score = rowMeans(pred_matrix)

# Write scores to output
write.table(final_score, file=output_file, row.names=FALSE, col.names=FALSE, sep=',')

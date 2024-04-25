
# ![legend](https://github.com/comingkms/MicrobiotAMR/assets/56736071/eb3e13ec-acb5-41c4-b2ec-6db0faf4f972) 
# An all-in-one amplicon-sequencing pipeline to corraltiveanalysis microbitoa and resistome
Input: PE reads or SE read from nanopore

EMU: Bacterial abundance


AMR: resistomeanalyzer https://github.com/cdeanj/resistomeanalyzer

R corrplot: correlation matrix 

# Install emu and AMR++ according to their documentation
....... Conda 

# Run emu on your input file to get the metagenomic abundance output -type 16s_PE or 16s_Nano
emu_output = "emu_output_file"

# Run xxxx on your input file to get the antimicrobial resistance genes output -type amr-PE 
amr_output = "amr_output_file"

# Import pandas or scipy to perform correlation analysis
import pandas as pd
import scipy.stats as stats

# Read the emu and AMRplusplus outputs as dataframes
emu_df = pd.read_csv(emu_output, sep="\t")
amr_df = pd.read_csv(amr_output, sep="\t")

# Merge the two dataframes on a common column, such as sample ID or bin ID
merged_df = pd.merge(emu_df, amr_df, on="sample_id")

# R script 

# Compute the matrix of p-value : further arguments to pass to the native R cor.test function
    # mat : is a matrix of data
cor.mtest <- function(mat, ...) {
    mat <- as.matrix(mat)
    n <- ncol(mat)
    p.mat<- matrix(NA, n, n)
    diag(p.mat) <- 0
    for (i in 1:(n - 1)) {
        for (j in (i + 1):n) {
            tmp <- cor.test(mat[, i], mat[, j], ...)
            p.mat[i, j] <- p.mat[j, i] <- tmp$p.value
        }
    }
  colnames(p.mat) <- rownames(p.mat) <- colnames(mat)
  p.mat
}
# matrix of the p-value of the correlation
M = cor(merged_df)
p.mat <- cor.mtest(M)

# Perform correlation analysis on the columns of interest, such as abundance or gene count
correlation = corrplot(M, type="upper", order="hclust", tl.col="black", tl.srt=45)

# Plot correlation matrix 
corrplot(M, type="upper", order="hclust", 
         p.mat = p.mat, sig.level = 0.01, insig = "blank")

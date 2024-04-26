
# ![legend](https://github.com/comingkms/MicrobiotAMR/assets/56736071/eb3e13ec-acb5-41c4-b2ec-6db0faf4f972) 
# An all-in-one amplicon-sequencing data analysis pipeline for resistome and microbiome

MicrobiotAMR(MAMR) is a simple python script that perform amplicon seqeucing data analyses for 16s rRNA gene and Illumina Antimicrobial Resistance(AMR) Research Panel, and corrliation analysis to identify 'potential' antimicrobial resistant bacteria.

+ [System requirements](#system-requirements)
+ [Installation](#installation)
+ [Usage](#usage)
+ [Output files](#output-files)
+ [Example](#example)
+ [Reference](#reference)  


## System requirements

MAMR has been developed and tested under a Linux environment.It requires certain tools and database in order to be installed and used: 
+ GNU bash (version 4 or later recommended)
+ [miniconda3](https://conda.io/en/latest/miniconda.html)


## Installation

The simplest (and recommended) way to install MAMR dependencies is through [conda](https://conda.io/en/latest/miniconda.html) in an isolated environment (*e.g.*, named `microbotAMR`):
```bash
git clone https://github.com/comingkms/MicrobiotAMR.git
cd MicrobiotAMR
conda env create -n microbiotAMR --file environment.yml
```
The whole installation process should take about 5-10 minutes.

To make the `microbiotAMR` command available, it is advised to include the absolute path of MAMR's directory in your PATH environment variable by adding the following line to your `~/.bashrc` file:

```
export PATH=/absolute/path/to/microbiotAMR:${PATH}
```


## Usage and command line options

Activate MAMR conda environment:
```
conda activate microbotAMR
```

Running microbotAMR:

Module 1: Analysis of  Illumina AMR reseach panel(AMR)

```
conda activate microbotAMR
```

Module 2: Analysis of 16s rRNA gene amplicon sequencing(16s)

```
conda activate microbotAMR
```
Module 3: corrliation analysis(COR)

```
conda activate microbotAMR
```

## Output files

The output directory of MAMR has the following structure:

Module 1: AMR 
```
OUTPUT_DIR/
├── strainberry_n2/
    ├── strainberry_n3/
├── ...
├── strainberry_nK/
├── assembly.scaffolds.bam
├── assembly.scaffolds.bam.bai
├── assembly.scaffolds.fa
└── assembly.scaffolds.fa.fai
```
Strainberry output assembly is stored in the `assembly.scaffolds.fa` file.

Module 2: 16s

```
OUTPUT_DIR/
├── strainberry_n2/
    ├── strainberry_n3/
├── ...
├── strainberry_nK/
├── assembly.scaffolds.bam
├── assembly.scaffolds.bam.bai
├── assembly.scaffolds.fa
└── assembly.scaffolds.fa.fai
```
Strainberry output assembly is stored in the `assembly.scaffolds.fa` file.

Module 3: COR

```
OUTPUT_DIR/
├── strainberry_n2/
    ├── strainberry_n3/
├── ...
├── strainberry_nK/
├── assembly.scaffolds.bam
├── assembly.scaffolds.bam.bai
├── assembly.scaffolds.fa
└── assembly.scaffolds.fa.fai
```
MAMR output assembly is stored in the `assembly.scaffolds.fa` file.

A minimap2-based alignment of input reads on the output assembly is also available in the `assembly.scaffolds.bam` file.

## Example

In order to verify that MAMR has been correctly installed, it is possible to test it on a small dataset in the `example` sub-directory.

### Name of raw read files

### Running MAMR


## Reference

If you use MAMR in your work, please cite:


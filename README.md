
# ![legend](https://github.com/comingkms/MicrobiotAMR/assets/56736071/eb3e13ec-acb5-41c4-b2ec-6db0faf4f972) 
# All-in-one amplicon-sequencing data analysis pipeline for resistome and microbiome

MicrobiotAMR(MAMR) is a simple python script that perform amplicon seqeucing data analyses for 16s rRNA gene and Illumina Antimicrobial Resistance(AMR) Research Panel, and corrliation analysis to identify 'potential' antimicrobial resistant bacteria.

+ [System requirements](#system-requirements)
+ [Installation](#installation)
+ [Usage](#usage)
+ [Output files](#output-files)
+ [Reference](#reference)  


## System requirements

MAMR has been developed and tested under a Linux environment.It requires certain tools and database in order to be installed and used:
+ Tool or pipleine:
+ [emu](https://github.com/treangenlab/emu)<sup>1</sup>
+ [fastp](https://github.com/OpenGene/fastp)<sup>2</sup>
+ [chopper](https://github.com/wdecoster/chopper)<sup>3</sup>
+ [resistomeanalyzer](https://github.com/cdeanj/resistomeanalyzer)
+ [Porechop](https://github.com/rrwick/Porechop)
+ [miniconda3](https://conda.io/en/latest/miniconda.html)
+ Python library:
  [glob](https://docs.python.org/3/library/glob.html)
  [shutil](https://docs.python.org/3/library/shutil.html)
  [argpare](https://docs.python.org/3/library/argparse.html)
  [panadas](https://pandas.pydata.org/)
  [numpy](https://numpy.org/)
  [cripy](https://github.com/EmanuelGoncalves/crispy)
  [termcolor](https://github.com/termcolor/termcolor)
  [tqdm](https://tqdm.github.io/)
+ Database:
+ micobiome database, which is [emu database](https://github.com/treangenlab/emu/tree/master/emu_database), can be found in the '16s_database' sub-directory or [Emu github](https://github.com/treangenlab/emu). 
+ AMR database, which is a hand-curated database based on [MEGARes V3.0 database](https://www.meglab.org/megares/)<sup>4</sup> and [Illumina AMR research panel documentation](https://www.illumina.com/products/by-brand/ampliseq/community-panels/antimicrobial-resistance.html#tabs-5bcafff4ef-item-28eba04f16-documentation), can be found in the 'AMR_database' sub-directory, respectively.
  

## Installation(...)

The simplest (and recommended) way to install MAMR dependencies is through [conda](https://conda.io/en/latest/miniconda.html) in an isolated environment (*e.g.*, named `microbotAMR`):
```bash
git clone https://github.com/comingkms/MicrobiotAMR.git
cd MicrobiotAMR
conda env create -n microbiotAMR --file environment.yml
```
The whole installation process should take about 5-10 minutes.

To make the `MAMR` command available, it is advised to include the absolute path of MAMR's directory in your PATH environment variable by adding the following line to your `~/.bashrc` file:

```
export PATH=/absolute/path/to/MAMR:${PATH}
```

## Usage and command line options

In order to verify that MAMR has been correctly installed, it is possible to test it on a small dataset in the `example` sub-directory.
### Name of raw read files
1. format of input files' name:
   PE: {sample_name}_Sxx_Lxxx_R1/R2.fastq.gz
   ONT:{sample_name}.fastq.gz 
2. Please make sure sample name is identical for the same sample for AMR and 16s rRNA gene amplicon sequencing data. 


Activate MAMR conda environment:
```
conda activate microbotAMR
```

Running microbotAMR:
```
$MAMR -h
usage: MAMR [-h] [-v] {AMR,BAC,COR} ...

Integrated microbiome and reistome analysis pipeline

positional arguments:
  {AMR,BAC,COR}  sub-commands
    AMR          Perform Illumina AMR research panel analysis
    BAC          Perform 16s rRNA gene amplicon sequencing analysis
    COR          Perform correlation analysis

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

Module 1: Analysis of  Illumina AMR reseach panel(AMR)

```
$MAMR AMR -h
usage: MAMR AMR [-h] -amr_db AMR_DATABASE -a ANNO_FILE -amr_q AMR_QUERY_FILES -amr_o AMR_OUTPUT [-t THREADS]

options:
  -h, --help            show this help message and exit
  -amr_db AMR_DATABASE, --AMR_database AMR_DATABASE
                        Path to AMR gene database
  -a ANNO_FILE, --anno_file ANNO_FILE
                        Annotation file for AMR database
  -amr_q AMR_QUERY_FILES, --AMR_query_files AMR_QUERY_FILES
                        Directory containing AMR query files
  -amr_o AMR_OUTPUT, --AMR_output AMR_OUTPUT
                        Output directory for AMR analysis results
  -t THREADS, --threads THREADS
                        Number of threads to use

```

Module 2: Analysis of 16s rRNA gene amplicon sequencing(BAC)

```
$MAMR BAC -h
usage: MAMR BAC [-h] -emu_db EMU_DATABASE -emu_q EMU_QUERY_FILES -qt {PE,ONT} -emu_o EMU_OUTPUT [-t THREADS]

options:
  -h, --help            show this help message and exit
  -emu_db EMU_DATABASE, --EMU_database EMU_DATABASE
                        Path to EMU database
  -emu_q EMU_QUERY_FILES, --EMU_query_files EMU_QUERY_FILES
                        Directory containing EMU query files
  -qt {PE,ONT}, --query_type {PE,ONT}
                        Type of query (PE or ONT)
  -emu_o EMU_OUTPUT, --EMU_output EMU_OUTPUT
                        Output directory for EMU analysis results
  -t THREADS, --threads THREADS
                        Number of threads to use

```
Module 3: corrliation analysis(COR)

```
$MAMR COR -h
usage: MAMR COR [-h] -cor_amr COR_INTPUT_AMR -cor_emu COR_INTPUT_EMU -cor_o COR_OUTPUT

options:
  -h, --help            show this help message and exit
  -cor_amr COR_INTPUT_AMR, --Cor_intput_AMR COR_INTPUT_AMR
                        Input directory containing AMR analysis combined results
  -cor_emu COR_INTPUT_EMU, --Cor_intput_EMU COR_INTPUT_EMU
                        Input directory containing EMU analysis combined results
  -cor_o COR_OUTPUT, --Cor_output COR_OUTPUT
                        Output directory for correlation analysis results

```

## Output files

The output directory of MAMR has the following structure:

Module 1: AMR 
```
OUTPUT_DIR/
├── Resistomes/
    ├── AMR_combined.class.csv
    ├── AMR_combined.gene.csv
    ├── AMR_combined.class_rel_abundance.csv
    ├── AMR_combined.gene_rel_abundance.csv
    ├──{sample_1}_sam.class.tsv 
    ├──{sample_1}_sam.gene.tsv
    ├──{sample_1}_sam.group.tsv
    ├──{sample_1}_sam.mechanism.tsv 
    ├──...

MAMR conbined outputs are stored in the `AMR_conbined.****.csv` files. 

Module 2: BAC

```
OUTPUT_DIR/
├── {sample_1}/
├── {sample_2}/
├── {sample_3}/
├── ...
├── combined/
    ├── {sample_1}_rel-abundance.tsv 
    ├── ...
    ├── emu-combined-genus.tsv
    ├── emu-combined-genus_counts.tsv
    ├── emu-combined-species.tsv
    └── emu-combined-species_counts.tsv
```
MAMR uses emu pipeline to analysis 16s rRNA sequencing data. please review Emu github](https://github.com/treangenlab/emu) for more inforamtion. 

Module 3: COR

```
OUTPUT_DIR/
├── correlation_genus.csv
├── correlation_species.csv
├── ...

```
MAMR correlation outputs are stored in the `corelation_xxx.csv' files. Other files in this output folder are copied from module1 and 2 output folders. 



## Citation 

If you use MAMR in your work, please cite:

## Reference

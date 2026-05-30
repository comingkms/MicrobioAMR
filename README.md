
#<img width="2167" height="726" alt="MicrobioAMR" src="https://github.com/user-attachments/assets/25796628-7790-419c-a8d8-d09e1727542e" />
 
# All-in-one pipeline designed to evaluate ampliconsequencing data for resistome and microbiome

MicrobiotAMR (MAMR) is a Python script that facilitates the analysis of amplicon sequencing data for the 16s rRNA gene and the Illumina Antimicrobial Resistance Research Panel, with the additional capability of performing correlation analysis to identify "potential" antimicrobial-resistant bacteria.

+ [System requirements](#system-requirements)
+ [Installation](#installation)
+ [Usage](#usage)
+ [Output files](#output-files)
+ [Citation](#citation)   
+ [Reference](#reference)  


## System requirements

MAMR was developed and tested in Ubuntu 22.04 under Python v3.10. It requires the installation and utilization of specific tools and databases.
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
  [scipy](https://pypi.org/project/scipy/)
  [termcolor](https://github.com/termcolor/termcolor)
  [tqdm](https://tqdm.github.io/)
  etc
+ Database:
  1. micobiome database, which is [emu database](https://github.com/treangenlab/emu/tree/master/emu_database), can be found in the [Emu github](https://github.com/treangenlab/emu). 
  2. AMR database, which is a hand-curated database based on [MEGARes V3.0 database](https://www.meglab.org/megares/)<sup>4</sup> and [Illumina AMR research panel documentation](https://www.illumina.com/products/by-brand/ampliseq/community-panels/antimicrobial-resistance.html#tabs-5bcafff4ef-item-28eba04f16-documentation), can be found in the 'AMR_database' sub-directory, respectively.
  

## Installation

The easiest and most convenient way to install MAMR dependencies is by using conda in an isolated environment, such as `microbotAMR`. This method ensures a smooth and hassle-free installation process.
```bash
git clone https://github.com/comingkms/MicrobiotAMR.git
cd MicrobiotAMR
conda env create -n microbiotAMR --file environment.yml
```
The whole installation process should take about 5-10 minutes.

To ensure the availability of the `MAMR` command, it is essential to add the absolute path of MAMR's directory to your PATH environment variable. This can be done by adding the following line to your `~/.bashrc` file:

```
export PATH=/absolute/path/to/MAMR:${PATH}
```

## Usage and command line options

To confirm the proper installation of MAMR, you can test a small dataset located in the `example` subdirectory.

Here are some guidelines for the file names of the raw read files:
1. For paired-end reads, the format of the input files' name should be: {sample_name}_Sxx_Lxxx_R1/R2_001.fastq.gz
2. For ONT reads, the format of the input file's name should be: {sample_name}.fastq.gz
3. For module 3(COR),  please ensure that the sample name matches the ones used for AMR and 16s rRNA gene amplicon sequencing.

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
  -bac_q BAC_QUERY_FILES, --BAC_query_files BAC_QUERY_FILES
                        Directory containing EMU query files
  -qt {PE,ONT}, --query_type {PE,ONT}
                        Type of query (PE or ONT)
  -bac_o BAC_OUTPUT, --BAC_output BAC_OUTPUT
                        Output directory for EMU analysis results
  -t THREADS, --threads THREADS
                        Number of threads to use

```
Module 3: correlation analysis(COR)

```
$MAMR COR -h
usage: MAMR COR [-h] -cor_amr COR_INTPUT_AMR -cor_emu COR_INTPUT_EMU -cor_o COR_OUTPUT

options:
  -h, --help            show this help message and exit
  -cor_amr COR_INTPUT_AMR, --Cor_intput_AMR COR_INTPUT_AMR
                        Input directory containing AMR analysis combined results
  -cor_bac COR_INTPUT_BAC, --Cor_intput_BAC COR_INTPUT_BAC
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
```
MAMR combined outputs are stored in the `AMR_conbined.****.csv` files. 

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
MAMR utilizes the Emu pipeline to analyze 16S rRNA sequencing data. For more information, please review the [Emu GitHub repository](https://github.com/treangenlab/emu) 

Module 3: COR

```
OUTPUT_DIR/
├── correlation_genus.csv
├── correlation_species.csv
├── ...

```
MAMR correlation results are saved in the `corelation_xxx.csv' files. The rest of the files in this output folder are copied from the output folders of modules 1 and 2.

## Citation 



## Reference
1. Curry KD, Wang Q, Nute MG, Tyshaieva A, Reeves E, Soriano S, Wu Q, Graeber E, Finzer P, Mendling W, Savidge T, Villapol S, Dilthey A, Treangen TJ. Emu: species-level microbial community profiling of full-length 16S rRNA Oxford Nanopore sequencing data. Nat Methods. 2022 Jul;19(7):845-853. doi: 10.1038/s41592-022-01520-4. Epub 2022 Jun 30. PMID: 35773532; PMCID: PMC9939874.
2. Chen S, Zhou Y, Chen Y, Gu J. fastp: an ultra-fast all-in-one FASTQ preprocessor. Bioinformatics. 2018 Sep 1;34(17):i884-i890. doi: 10.1093/bioinformatics/bty560. PMID: 30423086; PMCID: PMC6129281.
3. De Coster W, Rademakers R. NanoPack2: population-scale evaluation of long-read sequencing data. Bioinformatics. 2023 May 4;39(5):btad311. doi: 10.1093/bioinformatics/btad311. PMID: 37171891; PMCID: PMC10196664.
4. Bonin N, Doster E, Worley H, Pinnell LJ, Bravo JE, Ferm P, Marini S, Prosperi M, Noyes N, Morley PS, Boucher C. MEGARes and AMR++, v3.0: an updated comprehensive database of antimicrobial resistance determinants and an improved software pipeline for classification using high-throughput sequencing. Nucleic Acids Res. 2023 Jan 6;51(D1):D744-D752. doi: 10.1093/nar/gkac1047. PMID: 36382407; PMCID: PMC9825433.


<img width="2167" height="726" alt="MicrobioAMR" src="https://github.com/user-attachments/assets/25796628-7790-419c-a8d8-d09e1727542e" />
 
# All-in-one pipeline designed to evaluate amplicon sequencing data for resistome and microbiome analyses 

MicrobiotAMR (MAMR) is a Python script that facilitates the analysis of amplicon sequencing data for the 16s rRNA gene and the Illumina Antimicrobial Resistance Research Panel, with the additional capability of performing correlation analysis to identify "potential" antimicrobial-resistant bacteria.

+ [Requirements](#Requirements)
+ [Installation](#Installation)
+ [Test](#Test)
+ [Usage](#Usage)
+ [Output](#Output) 
+ [Reference](#Reference)  


## Requirements

MAMR was developed and tested in Ubuntu 22.04 under Python v3.10. It requires the installation and utilization of specific tools and databases.
+ Pipleine or tool:
   + [emu](https://github.com/treangenlab/emu)<sup>1</sup>: microbiome and resistome (alignment parsing code adapted from emu) analyses  
   + [fastp](https://github.com/OpenGene/fastp)<sup>2</sup>: microbiome and resistome analyses 
   + [chopper](https://github.com/wdecoster/chopper)<sup>3</sup>: microbiome analysis 
   + [gunzip](https://github.com/azerella/gunzip): microbiome analysis
   + [Porechop](https://github.com/rrwick/Porechop): microbiome analysis
   + [bwa-mem2](https://github.com/bwa-mem2/bwa-mem2)<sup>4</sup>: resistome analysis 
+ Python standard library plus:
  [scikit-learn](https://github.com/scikit-learn/scikit-learn)
  [kneed](https://pypi.org/project/kneed/)
  [pysam](https://github.com/pysam-developers/pysam)
  [panadas](https://pandas.pydata.org/)
  [numpy](https://numpy.org/)
  [scipy](https://pypi.org/project/scipy/)
  [termcolor](https://github.com/termcolor/termcolor)
  [tqdm](https://tqdm.github.io/)
+ Database:
    + The Emu database, is available for download on the [Emu GitHub page](https://github.com/treangenlab/emu) and save it to the Emu_database directory.
    + The AMR database curated in this study,  based on AMR database inlcuding CARD<sup>5</sup>, NCBI<sup>6</sup>, ResFinder<sup>7</sup>, and MEGARes<sup>8</sup>, is located in the 'AMR_database' subdirectory.
  

## Installation

The easiest and most convenient way to install MAMR dependencies is by using conda in an isolated environment, such as `MAMR`. This method ensures a smooth and hassle-free installation process.
```bash
git clone https://github.com/comingkms/MicrobioAMR.git
chmod +x MicrobioAMR/MAMR
cd MicrobioAMR
conda env create -f MAMR.yml
conda activate MAMR
```
The whole installation process should take about 5-10 minutes.

To ensure the availability of the `MAMR` command, it is essential to add the absolute path of MAMR's directory to your PATH environment variable. This can be done by adding the following line to your `~/.bashrc` file:

```
echo 'export PATH="/absolute/path/to/MAMR:$PATH"'>> ~/.bashrc && source ~/.bashrc
```
## Test
1. Run the run_test.py 
```
pytest -v -s test/run_test.py
```
2. Results(example):
```
pytest -v -s test/run_test.py
====================================test session starts ===========================
platform linux -- Python 3.10.12, pytest-9.0.3, pluggy-1.6.0 -- /home/comingkms/anaconda3/envs/microbioteAMR/bin/python
cachedir: .pytest_cache
rootdir: /mnt/Mydata/kms/resistomeanalyzer/AMR/test
collected 7 items                                                                                                                                                                                                                  

test/run_test.py::test_layout 
Project root: /mnt/Mydata/kms/resistomeanalyzer/AMR/test
Test root: /mnt/Mydata/kms/resistomeanalyzer/AMR/test/test
MAMR: /mnt/Mydata/kms/resistomeanalyzer/AMR/test/MAMR_9
AMR database: /mnt/Mydata/kms/resistomeanalyzer/AMR/test/AMR_database/AmpliSeq_amr_database_4.fasta
AMR annotation: /mnt/Mydata/kms/resistomeanalyzer/AMR/test/AMR_database/Tax_final_15.csv
BAC database: /mnt/Mydata/kms/resistomeanalyzer/AMR/test/Emu_database
COR data: /mnt/Mydata/kms/resistomeanalyzer/AMR/test/COR_data
AMR input: /mnt/Mydata/kms/resistomeanalyzer/AMR/test/test/AMR
BAC input: /mnt/Mydata/kms/resistomeanalyzer/AMR/test/test/BAC
PASSED
==================================================================================                                                                                                                                                  
test/run_test.py::test_python_dependency 
Python dependencies: {'pandas': '2.2.3', 'numpy': '2.2.4', 'scipy': '1.15.1', 'termcolor': '2.3.0', 'tqdm': '4.66.2', 'pysam': '0.21.0', 'kneed': '0.8.5', 'scikit-learn': '1.5.0'}
PASSED
==================================================================================                                                                                                                                                  
test/run_test.py::test_external_pipeline 
External pipelines: {'fastp': 'fastp 0.23.4', 'bwa-mem2': '2.2.1', 'porechop': '0.2.4', 'gunzip': 'gunzip (gzip) 1.10', 'chopper': 'chopper 0.7.0', 'emu': 'emu v3.4.5'}
PASSED
==================================================================================
test/run_test.py::test_MAMR 
MAMR_9 v0.9.10_May_2026
PASSED
==================================================================================
test/run_test.py::test_AMR 
Output: /tmp/pytest-of-comingkms/pytest-0/mamr_amr0/AMR_output/Resistomes/AMR_gene_combined.csv
Samples: ['Test-2', 'Test-1']
PASSED
==================================================================================
test/run_test.py::test_BAC 
Genus: /tmp/pytest-of-comingkms/pytest-0/mamr_bac0/BAC_output/combined/emu-combined-genus.tsv
Species: /tmp/pytest-of-comingkms/pytest-0/mamr_bac0/BAC_output/combined/emu-combined-species.tsv
Sample files: ['Test-2_rel-abundance.tsv', 'Test-1_rel-abundance.tsv']
PASSED
==================================================================================
test/run_test.py::test_COR 
Input dir: /mnt/Mydata/kms/resistomeanalyzer/AMR/test/COR_data
Gene output: /tmp/pytest-of-comingkms/pytest-0/test_COR0/COR_output/correlation_genus_gene.csv
family output: /tmp/pytest-of-comingkms/pytest-0/test_COR0/COR_output/correlation_genus_family.csv
PASSED
==================================================================================                                                                                                                                                  

======================7 passed in 80.76s (0:01:20) ===============================
```
## Usage 

Here are some guidelines for file names of the raw read files:
1. For paired-end reads, the format of the input files' name should be: {sample_name}_Sxx_Lxxx_R1/R2_001.fastq.gz(Illumina standard format ) 
2. For ONT reads, the format of the input file's name should be: {sample_name}.fastq.gz
3. For module COR,  please ensure that the sample name matches the ones used for AMR and BAC moudels.

Activate MAMR conda environment:
```
conda activate MAMR
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

Module 1: Analysis of Illumina AMR reseach panel(AMR)

```
$MAMR AMR -h
usage: MAMR AMR [-h] -amr_db AMR_DATABASE -a ANNO_FILE -amr_q AMR_QUERY_FILES -amr_o AMR_OUTPUT [-t THREADS] [-m {1,2,3}]

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
  -m {1,2,3}, --filtering_mode {1,2,3}
                        Low-abundance filtering mode (default: 2): 1 = specific; 2 = balanced; 3 = sensitive

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

## Output

The output directory of MAMR has the following structure:

Module 1: AMR 
```
OUTPUT_DIR/
├── Resistomes/
    ├── AMR_gene_combined.csv
    ├── temp_output/
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

## Reference
1. Curry KD, Wang Q, Nute MG, Tyshaieva A, Reeves E, Soriano S, Wu Q, Graeber E, Finzer P, Mendling W, Savidge T, Villapol S, Dilthey A, Treangen TJ. Emu: species-level microbial community profiling of full-length 16S rRNA Oxford Nanopore sequencing data. Nat Methods. 2022 Jul;19(7):845-853. doi: 10.1038/s41592-022-01520-4. Epub 2022 Jun 30. PMID: 35773532; PMCID: PMC9939874.
2. Chen S, Zhou Y, Chen Y, Gu J. fastp: an ultra-fast all-in-one FASTQ preprocessor. Bioinformatics. 2018 Sep 1;34(17):i884-i890. doi: 10.1093/bioinformatics/bty560. PMID: 30423086; PMCID: PMC6129281.
3. De Coster W, Rademakers R. NanoPack2: population-scale evaluation of long-read sequencing data. Bioinformatics. 2023 May 4;39(5):btad311. doi: 10.1093/bioinformatics/btad311. PMID: 37171891; PMCID: PMC10196664.
4. Vasimuddin Md, Sanchit Misra, Heng Li, Srinivas Aluru. Efficient Architecture-Aware Acceleration of BWA-MEM for Multicore Systems. IEEE Parallel and Distributed Processing Symposium (IPDPS), 2019. 10.1109/IPDPS.2019.00041
5. Brian P Alcock, William Huynh, Romeo Chalil, et al. CARD 2023: expanded curation, support for machine learning, and resistome prediction at the Comprehensive Antibiotic Resistance Database, Nucleic Acids Research, Volume 51, Issue D1, 6 January 2023, Pages D690–D699, https://doi.org/10.1093/nar/gkac920
6. Feldgarden, M., Brover, V., Gonzalez-Escalona, N. et al. AMRFinderPlus and the Reference Gene Catalog facilitate examination of the genomic links among antimicrobial resistance, stress response, and virulence. Sci Rep 11, 12728 (2021). https://doi.org/10.1038/s41598-021-91456-0
7. Florensa AF, Kaas RS, Clausen PTLC, Aytan-Aktug D, Aarestrup FM. ResFinder - an open online resource for identification of antimicrobial resistance genes in next-generation sequencing data and prediction of phenotypes from genotypes. Microb Genom. 2022 Jan;8(1):000748. doi: 10.1099/mgen.0.000748. PMID: 35072601; PMCID: PMC8914360.
8. Bonin N, Doster E, Worley H, Pinnell LJ, Bravo JE, Ferm P, Marini S, Prosperi M, Noyes N, Morley PS, Boucher C. MEGARes and AMR++, v3.0: an updated comprehensive database of antimicrobial resistance determinants and an improved software pipeline for classification using high-throughput sequencing. Nucleic Acids Res. 2023 Jan 6;51(D1):D744-D752. doi: 10.1093/nar/gkac1047. PMID: 36382407; PMCID: PMC9825433.

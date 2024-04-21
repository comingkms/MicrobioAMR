import os
import subprocess
import glob
import shutil
import argparse
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from termcolor import colored
import seaborn as sns


# Program : MicrobiomeAMR
# Author: Mingsong Kang (mingsong.kang@inspection.gc.ca)
# Installation:
# 1.Conda: EMU, minimap2, fastp, chopper, and resistomeanalyzer, Porechop, Filtlong
# 2.Python packages: sutil, argpares, panadas, numpy, scipy, termcolor, and seaborn
# input files format   1. PE: *_R1/R2.fastq.gz. ONT:*.fastq.gz; * = sample name.
#                      2. use the same name of the same sample for 16S and AMR fastq files
# V6 improve the sample name.


# Paths to Additional tools/scripts and check if they are installed and found in path
EMU = subprocess.run(['which', 'emu'], capture_output=True, text=True).stdout.strip()
if not EMU:
    print("ERROR: Cannot find emu script using 'which emu'")
    exit(1)

Resistome = subprocess.run(['which', 'resistome'], capture_output=True, text=True).stdout.strip()
if not Resistome:
    print("ERROR: Cannot find Resistome script using 'which resistomeanalyzer'")
    exit(1)

minimap2 = subprocess.run(['which', 'minimap2'], capture_output=True, text=True).stdout.strip()
if not minimap2:
    print("ERROR: Cannot find minimap2 script using 'which minimap2'")
    exit(1)
fastp = subprocess.run(['which', 'fastp'], capture_output=True, text=True).stdout.strip()
if not fastp:
    print("ERROR: Cannot find fastp using 'which fastp'")
    exit(1)
pTrimmer = subprocess.run(['which', 'ptrimmer'], capture_output=True, text=True).stdout.strip()
if not pTrimmer:
    print("ERROR: Cannot find pTrimmer using 'which ptrimmer'")
    exit(1)

chopper = subprocess.run(['which', 'chopper'], capture_output=True, text=True).stdout.strip()
if not chopper:
    print("ERROR: Cannot find pTrimmer using 'which chopper'")
    exit(1)

gunzip = subprocess.run(['which', 'gunzip'], capture_output=True, text=True).stdout.strip()
if not gunzip:
    print("ERROR: Cannot find pTrimmer using 'which gunzip'")
    exit(1)
gzip = subprocess.run(['which', 'gzip'], capture_output=True, text=True).stdout.strip()
if not gunzip:
    print("ERROR: Cannot find pTrimmer using 'which gzip'")
    exit(1)

# Default values, unless denoted when running MicrobiomeAMR
AMR_database = ""
anno_file = ""
AMR_query_files = ""
EMU_query_files = ""
query_type = ""
threads = "1"
AMR_output = ""
EMU_output = ""
EMU_database = ""
Cor_output = ""
Cor_intput_AMR = ""
Cor_intput_EMU = ""
fastp_output = ""
fastp_output_dir = ""


if __name__ == "__main__":
    __version__ = "1.3.0"
# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--version', '-v', action='version', version='%(prog)s v' + __version__)
subparsers = parser.add_subparsers(dest="subparser_name", help='sub-commands')

#AMR function
AMR_parser = subparsers.add_parser("AMR", help="Generate AMR gene abundance estimates")
AMR_parser.add_argument('-amr_db', '--AMR_database', help='Path to AMR database')
AMR_parser.add_argument('-a', '--anno_file', help='AMR annotation file')
AMR_parser.add_argument('-amr_q', '--AMR_query_files', help='Path to query AMR fastq files')
AMR_parser.add_argument('-amr_o', '--AMR_output', help='AMR Output for AMR genes qualification')
AMR_parser.add_argument('-t', '--threads', help='Number of threads')
AMR_parser.add_argument('-i', '--input', help='input file containing sample names, fastq files paths [.txt]')

#EMU function
EMU_parser = subparsers.add_parser("EMU", help="Generate bacterial abundance estimates")
EMU_parser.add_argument('-emu_db', '--EMU_database', help='Path to EMU database')
EMU_parser.add_argument('-qt', '--query_type', help='Information for PE or ONT')
EMU_parser.add_argument('-emu_q', '--EMU_query_files', help='Path to query 16S fastq files')
EMU_parser.add_argument('-emu_o', '--EMU_output', help='EMU Output for microbial community ')
EMU_parser.add_argument('-t', '--threads', help='Number of threads')
EMU_parser.add_argument('-i', '--input', help='input file containing sample names, fastq files paths [.txt]')

#Correlation function
Cor_parser = subparsers.add_parser("COR", help="Correlation analysis between AMR gene abundances and bacterial abundances")
Cor_parser.add_argument('-cor_i_amr', '--Cor_intput_AMR', help="Path to the folder containing AMR_combined_rel-abundance file")
Cor_parser.add_argument('-cor_i_emu', '--Cor_intput_EMU', help="Path to the folder containing EMU_combined_rel-abundance file")
Cor_parser.add_argument('-cor_o', '--Cor_output', help='Correlation Output for microbial community ')
#parser.add_argument('-t', '--threads', help='Number of threads')

args = parser.parse_args()

# AMR gene abundance
if args.subparser_name == "AMR":
   AMR_database = args.AMR_database
   AMR_query_files = args.AMR_query_files
   AMR_output_dir = AMR_output
   anno_file = args.anno_file
   input_file= args.input

   if not AMR_database:
       print("ERROR: Path to AMR database not found, assign using -amr_db")
       exit(1)

   if not anno_file:
        print("ERROR: No AMR annotation file, assign using -a")
        exit(1)

 #  if not AMR_query_files:
  #     print("ERROR: Path to query AMR fastq files not found, assign using -amr_q")
   #    exit(1)

   if not input_file:
       print("ERROR: input file not found, assign using -i")
       exit(1)

   if args.AMR_output:
       AMR_output = args.AMR_output
   else:
       print("ERROR: Amr output not specified, assign using -amr_o")
       exit(1)

   if os.path.exists(AMR_output_dir):
       print("ERROR: AMR output directory already exists, please remove or set alternate output")
       exit(1)

   os.mkdir(AMR_output)
   os.chdir(AMR_output_dir)
   print("\n  \n")
   print(colored("##############################", 'yellow'))
   print(colored("#", 'yellow'), colored("QC checks and adaptors removal", 'red'), colored("#", 'yellow'))
   print(colored("##############################", 'yellow'))
   print("\n  \n")
   # Read the contents of the TXT file


with open(input_file, "r") as file:
  next(file)
  for line in file:
    # Split the line into sample and file paths using tabs
    sample, r1_amr_path, r2_amr_path, r1_16s_path, r2_16s_path = line.strip().split("\t")

    subprocess.run([
        "fastp",
        "-i",  r1_amr_path,
        "-I",  r2_amr_path,
        "-o",   f"{sample}_R1_trimed.fastq.gz",
        '-O',   f"{sample}_R2_trimed.fastq.gz",
        '-c',
        #"-f", "20",# need some data to confirmed it
        #"-t", "5", # need some data to confirmed it
        "-h", f"{sample}_amr_fastp.htmp",
        #"-j", f"{sample}_fastp.json",
        "-w", threads

   ])

print("\n  \n")
print(colored('QC checks and adaptor removal were completed', 'red'))
print('--------------------------------------------')
print("\n  \n")
print("\n  \n")
print(colored("################", 'yellow'))
print(colored("#", 'yellow'),colored("primers trimming", 'red'), colored("#", 'yellow'))
print(colored("################", 'yellow'))
print("\n  \n")
# Generation of SAM files using minimap2
print(colored("############################", 'yellow'))
print(colored("#", 'yellow'), colored("Alignment using minimap2", 'red'), colored("#", 'yellow'))
print(colored("############################", 'yellow'))
print("\n  \n")
   # os.chdir(AMR_query_files)
   # if query_type == "PE":
for file in glob.glob("*_R1_trimed.fastq.gz"):
       m = file.replace("_R1_trimed.fastq.gz", "")
       subprocess.run(
           ['minimap2', '-ax', 'sr', AMR_database, f'{m}_R1_trimed.fastq.gz', f'{m}_R2_trimed.fastq.gz', '-t', threads],
           stdout=open(f'{m}.sam', 'w'))


print("\n  \n")
print(colored("Sam files were generated and transferred to the AMR output folder", 'red'))
print('-----------------------------------------------------------------')
print("\n  \n")
print(colored("#################################", 'yellow'))
print(colored("#", 'yellow'), colored("Characterization of Resistome", 'red'), colored("#", 'yellow'))
print(colored("#################################", 'yellow'))
print("\n  \n")


os.mkdir('Resistomes')

for j in glob.glob("*.sam"):
       gene_fp = f"{j}.gene.tsv"
       group_fp = f"{j}.group.tsv"
       mech_fp = f"{j}.mechanism.tsv"
       class_fp = f"{j}.class.tsv"
       type_fp = f"{j}.type.tsv"
       threshold = "80"
       command_re = [
           "resistome",
           "-ref_fp", AMR_database,
           "-sam_fp", j,
           "-annot_fp", anno_file,
           "-gene_fp", gene_fp,
           "-group_fp", group_fp,
           "-class_fp", class_fp,
           "-mech_fp", mech_fp,
           "-t", threshold
       ]

       subprocess.run(command_re)
       shutil.move(group_fp, "Resistomes")
       shutil.move(gene_fp, "Resistomes")
       shutil.move(class_fp, "Resistomes")
       shutil.move(mech_fp, "Resistomes")


# Combine outputs from  mutiple files( adopted from codes from AMR++)
os.chdir(AMR_output + '/Resistomes')
file_name_list = os.listdir(AMR_output + '/Resistomes')
input_files = [os.path.join(AMR_output + '/Resistomes', file)
               for file in file_name_list if file.endswith('.gene.tsv')]
output_file = 'AMR_combined.gene.csv'

os.chdir(AMR_output + '/Resistomes')
file_name_list = os.listdir(AMR_output + '/Resistomes')
input_files_1 = [os.path.join(AMR_output + '/Resistomes', file)
                  for file in file_name_list if file.endswith('.class.tsv')]
output_file_1 = 'AMR_combined.class.csv'
# combined data for gene
   samples = {}
   labels = set()
   for file in file_name_list:
    if file.endswith(".gene.tsv"):
       with open(file, 'r') as f:
           data = f.read().split('\n')[1:]
           for entry in data:
               if not entry:
                   continue
               entry = entry.split('\t')
               sample = entry[0].split('.')[0]
               count = float(entry[2])
               gene_name = entry[1]
               try:
                   samples[sample][gene_name] = count
               except KeyError:
                   try:
                       samples[sample].setdefault(gene_name, count)
                   except KeyError:
                       samples.setdefault(sample, {gene_name: count})
               labels.add(gene_name)

   with open(output_file, 'w') as amr:
       local_sample_names = []
       for sample, dat in samples.items():
           local_sample_names.append(sample)
       amr.write('name' + '\t' + '\t'.join(local_sample_names) + '\n')
       for label in labels:
           local_counts = []
           amr.write(label + '\t')
           for local_sample in local_sample_names:
               if label in samples[local_sample]:
                   local_counts.append(str(samples[local_sample][label]))
               else:
                   local_counts.append(str(0))
           amr.write('\t'.join(local_counts) + '\n')

# Conbined data for class

samples = {}
labels = set()
for file in file_name_list:
    if file.endswith(".class.tsv"):
        with open(file, 'r') as f:
            data = f.read().split('\n')[1:]
            for entry in data:
                if not entry:
                    continue
                entry = entry.split('\t')
                sample = entry[0].split('.')[0]
                count = float(entry[2])
                class_name = entry[1]
                try:
                    samples[sample][class_name] = count
                except KeyError:
                    try:
                        samples[sample].setdefault(class_name, count)
                    except KeyError:
                        samples.setdefault(sample, {class_name: count})
                labels.add(class_name)

with open(output_file_1, 'w') as amr:
    local_sample_names = []
    for sample, dat in samples.items():
        local_sample_names.append(sample)
    amr.write('name' + '\t' + '\t'.join(local_sample_names) + '\n')
    for label in labels:
        local_counts = []
        amr.write(label + '\t')
        for local_sample in local_sample_names:
            if label in samples[local_sample]:
                local_counts.append(str(samples[local_sample][label]))
            else:
                local_counts.append(str(0))
        amr.write('\t'.join(local_counts) + '\n')


    # Change read counts to relative abundance
   amr_data = pd.read_csv(output_file, sep="\t")
   amr_data_1 = pd.read_csv(output_file_1, sep="\t")
   # Get the bacterial names from the first column
   Amr_gene_names = amr_data.iloc[:, 0]
   Amr_class_names = amr_data_1.iloc[:, 0]
   # Calculate the sum of counts for each sample (column)
   sample_sums = amr_data.iloc[:, 1:].sum(axis=0)
   sample_sums_1 = amr_data_1.iloc[:, 1:].sum(axis=0)
   # Calculate the relative abundance for each sample
   relative_abundance = amr_data.iloc[:, 1:].div(sample_sums, axis=1)
   relative_abundance_1 = amr_data_1.iloc[:, 1:].div(sample_sums, axis=1)
   # Create a new DataFrame with bacterial names and relative abundance
   result = pd.concat([Amr_gene_names, relative_abundance], axis=1)
   result_1 = pd.concat([Amr_class_names, relative_abundance_1], axis=1)
   # Save the results to a new CSV file
   result.to_csv('AMR_gene_combined_rel-abundance.csv', sep='\t', index=False)
   result_1.to_csv('AMR_class_combined_rel-abundance.csv', sep='\t', index=False)

#Clean up: move all the temp files to a folder
   os.chdir(AMR_query_files)
   os.mkdir('temp_output')
t_output_dir = AMR_query_files +'/temp_output'
for f in glob.glob('*.sam'):
       shutil.move(f, t_output_dir)
for f in glob.glob('*_trimed.fastq.gz'):
       shutil.move(f, t_output_dir)
for f in glob.glob('*.htmp'):
       shutil.move(f, t_output_dir)
for f in glob.glob('*.json'):
       shutil.move(f, t_output_dir)
for f in glob.glob('*.fastq'):
       shutil.move(f, t_output_dir)
for f in glob.glob('*.ampcount'):
       shutil.move(f, t_output_dir)

print('---------------------------------------------------------')
print(colored("Analysis of AMR gene abundances  profiling was completed ", 'red'))
print('---------------------------------------------------------')



#Bacterial abundance

if args.subparser_name == "EMU":
   EMU_query_files = args.EMU_query_files
   EMU_database = args.EMU_database
   query_type = args.query_type
   threads = args.threads
   EMU_output_dir = EMU_output
   #primers = args.primers
   if not EMU_database:
       print("Path to EMU database not found, assign using -emu_db")
       exit(1)

   if not EMU_query_files:
       print("Path to query 16S fastq files not found, assign using -emu_q")
       exit(1)

   if not query_type:
       print("ERROR: No information for PE or ONT, assign using -qt")
       exit(1)

   if args.EMU_output:
      EMU_output = args.EMU_output
   else:
      print("EMU output not specified, assign using -emu_o")
      exit(1)

   if os.path.exists(EMU_output_dir):
       print("ERROR: EMU output directory already exists, please remove or set alternate output")
       exit(1)


with open("sample_file.txt", "r") as file:
lines = file.readlines()

   print("\n  \n")
   print(colored("###################", 'yellow'))
   print(colored("#", 'yellow'), colored("QC checks and trims", 'red'), colored("#", 'yellow'))
   print(colored("###################", 'yellow'))
   print("\n  \n")
   os.mkdir(EMU_output)
   os.chdir(EMU_query_files)
 if query_type == "PE":
   for line in lines:
    # Split the line into sample and file paths using tabs
     sample, r1_amr_path, r2_amr_path, r1_16s_path, r2_16s_path = line.strip().split("\t")

     subprocess.run([
               "fastp",
               "-i", r1_16s_path,
               "-I", r2_16s_path,
               "-o", f"{sample}_R1_trimed.fastq.gz",
               "-O", f"{sample}_R2_trimed.fastq.gz",
               #"-f", "20",
               #"-t", "5",
               "-h", f"{sample}_16s_fastp.htmp",
               #"-j", f"{j}_fastp.json",
               "-w", threads
           ])
 elif query_type == "ONT":
   for line in lines:
        # Split the line into sample and file paths using tabs
      sample, r1_amr_path, r2_amr_path, r1_16s_path, r2_16s_path = line.strip().split("\t")

      subprocess.run([
               "porechop",
               "-i", r1_16s_path,
               "-o", f"{sample}_trimed.fastq.gz"

           ])

   for file in glob.glob("*_trimed.fastq.gz"):
           i = file.replace("_trimed.fastq.gz", "")
           gunzip_process = subprocess.Popen(["gunzip", "-c", f"{i}_trimed.fastq.gz"], stdout=subprocess.PIPE)
           nanofilt_process = subprocess.Popen(["chopper", "-q", "10", "--minlength", "1000", "--maxlength", "2000"],
                                               stdin=gunzip_process.stdout, stdout=subprocess.PIPE)
           gzip_process = subprocess.Popen(["gzip", "-c"], stdin=nanofilt_process.stdout, stdout=subprocess.PIPE)

           with open(f"{i}_f_trimed.fastq.gz", "wb") as f:
               f.write(gzip_process.communicate()[0])



   print("\n  \n")
   print(colored('QC checks and adaptors/primers trims were completed', 'red'))
   print('---------------------------------------------------')
   print("\n  \n")
   #os.chdir(EMU_query_files)

   print(colored("############################################", 'yellow'))
   print(colored("#", 'yellow'), colored("Characterization of microbiome using EMU", 'red'), colored("#", 'yellow'))
   print(colored("############################################", 'yellow'))

 if query_type == "PE":
       for file in glob.glob("*_R1_p_trimed.fastq"):
           j = file.replace("_R1_p_trimed.fastq", "")
           subprocess.run([
               "emu", "abundance",
               "--type", "sr",
               f"{j}_R1_trimed.fastq.gz",
               f"{j}_R2_trimed.fastq.gz",
               "--db", EMU_database,
               "--threads", threads,
               "--keep-counts",
               "--min-abundance", '0.0005',
               "--output-dir", f"{EMU_output}/{j}"
           ])
 elif query_type == "ONT":
       for file in glob.glob("*_f_trimed.fastq.gz"):
           j = file.replace("_f_trimed.fastq.gz", "")
           subprocess.run([
               "emu", "abundance",
               f"{j}_f_trimed.fastq.gz",
               "--db", EMU_database,
               "--threads", threads,
               "--keep-counts",
               "--min-abundance", '0.0001',
               "--output-dir", f"{EMU_output}/{j}"
           ])
   # Combine EMU outputs
   os.chdir(EMU_output)
   os.mkdir('combined')
   pattern = '*_f_trimed.fastq_rel-abundance.tsv'

   file_paths = glob.glob(os.path.join(EMU_output, '**', pattern), recursive=True)

   # Move each file to the destination directory
   for file_path in file_paths:
       # Extract the filename from the file path
       filename = os.path.basename(file_path)
       # Construct the destination file path
       destination_path = os.path.join(EMU_output + '/combined', filename)
       # Move the file to the destination directory
       shutil.move(file_path, destination_path)

   os.chdir(EMU_output + '/combined')

   file_paths = glob.glob("*_f_trimed.fastq_rel-abundance.tsv'")

   for old_filepath in file_paths:
       # Extract the filename from the file path
       old_filename = os.path.basename(old_filepath)
       # Split the filename into parts
       parts = old_filename.split('_')
       # Remove the last two parts from the filename
       new_parts = parts[:-3]
       # Add the suffix to the new filename
       new_filename = '_'.join(new_parts) + '_rel-abundance.tsv'
       # Rename the file
       os.rename(old_filename, new_filename)

   os.chdir(EMU_output)
   print("\n  \n")
   print(colored("#######################################", 'yellow'))
   print(colored("#", 'yellow'), colored("Combined tables are being generated", 'red'), colored("#", 'yellow'))
   print(colored("#######################################", 'yellow'))
   print("\n  \n")
   subprocess.run(['emu', 'combine-outputs', 'combined', 'tax_id'])
   subprocess.run(['emu', 'combine-outputs', 'combined', 'genus'])
   subprocess.run(['emu', 'combine-outputs', 'combined', 'tax_id', '--counts'])
   subprocess.run(['emu', 'combine-outputs', 'combined', 'genus', '--counts'])

# Clean up: move all the temp files to a folder
   os.chdir(EMU_query_files)
   os.mkdir('fastp_output')
   fastp_output_dir = EMU_query_files + '/fastp_output'
   for f in glob.glob('*.sam'):
       shutil.move(f, fastp_output_dir)
   for f in glob.glob('*_trimed.fastq.gz'):
       shutil.move(f, fastp_output_dir)
   for f in glob.glob('*.htmp'):
       shutil.move(f, fastp_output_dir)
   print("\n  \n")
   print(colored("Microbiome analysis has been completed", 'red'))
   print('--------------------------------------')



# Correlation analysis

if args.subparser_name == "COR":
    Cor_output_dir = Cor_output

    if args.Cor_intput_AMR:
        Cor_intput_AMR = args.Cor_intput_AMR
    else:
      print("AMR intput not specified, assign using -cor_i_amr")
      exit(1)
    if args.Cor_intput_EMU:
        Cor_intput_EMU = args.Cor_intput_EMU
    else:
        print("AMR intput not specified, assign using -cor_i_emu")
        exit(1)

    if args.Cor_output:
        Cor_output = args.Cor_output
    else:
      print("EMU output not specified, assign using -cor_o")
      exit(1)

    print("\n  \n")
    print(colored("########################", 'yellow'))
    print(colored("#", 'yellow'), colored("Correlation analysis", 'red'), colored("#", 'yellow'))
    print(colored("########################", 'yellow'))
    print("\n  \n")

    # Transfer data from AMR AND EMU to corrlation output folder
    os.mkdir(Cor_output)

    os.chdir(Cor_intput_AMR)
    shutil.move('AMR_combined_rel-abundance.csv', Cor_output)

    os.chdir(Cor_intput_EMU)
    shutil.move('emu-combined-genus.tsv', Cor_output)

    os.chdir(Cor_output)
    # Combine rel_abudance files

    print("\n Combine bacterial and AMR genes counts \n")
    # Read bacterial abundance file
    bacterial_file = 'emu-combined-genus.tsv'
    bacterial_df = pd.read_csv(bacterial_file, sep="\t", header=0, index_col=0)
    # Only keep genus column
    genus = bacterial_df.drop(columns=['family', 'order', 'class', 'phylum', 'superkingdom'])
    genus = genus.reset_index()
    genus = genus.dropna(axis=0)
    genus = genus.set_index('genus')
    genus = genus.drop("unassigned")
    genus_t = np.transpose(genus)

    # Read AMR gene abundance file
    amr_file = 'AMR_combined_rel-abundance.csv'
    amr_df = pd.read_csv(amr_file, sep="\t", index_col=0, header=0)
    amr_t = np.transpose(amr_df)

    # Merge
    merged_df = pd.merge(genus_t, amr_t, left_index=True, right_index=True)

    # Correlation analysis

    cor = merged_df.corr()

    # cor_1 = cor.drop(list(genus_t.columns))
    # cor_2 = cor_1.drop(list(amr_t.columns),axis = 1)

    print("\n P-value calculation \n")


    # p-value calculation https://www.statology.org/p-value-correlation-pandas/
    def r_pvalues(df):
        cols = pd.DataFrame(columns=df.columns)
        p = cols.transpose().join(cols, how='outer')
        for r in df.columns:
            for c in df.columns:
                tmp = df[df[r].notnull() & df[c].notnull()]
                p[r][c] = round(pearsonr(tmp[r], tmp[c])[1], 4)
        return p


    pvalue = r_pvalues(merged_df)


    # pvalue_1 = pvalue.drop(list(genus_t.columns))
    # pvalue_2 = pvalue_1.drop(list(amr_t.columns),axis = 1)

    # Combine cor and p vaule (http://www.sthda.com/english/wiki/correlation-matrix-a-quick-start-guide-to-analyze-format-and-visualize-a-correlation-matrix-using-r-software)

    def flattenCorrMatrix(cormat, pmat):

        ut = np.triu_indices(len(cormat), 1)  # get the upper triangular indices

        data = {

            "row": cormat.index[ut[0]],  # get the row names

            "column": cormat.index[ut[1]],  # get the column names

            "cor": cormat.values[ut],  # get the correlation values

            "p": pmat.values[ut]  # get the p values

        }

        return pd.DataFrame(data)  # return a data frame


    print("\n Remove duplications and generate correlation file and figure \n")
    # remove duplications
    cor_p = flattenCorrMatrix(cor, pvalue)
    cor_p_1 = cor_p[~cor_p.row.isin(list(amr_t.columns))]
    cor_p_2 = cor_p_1[~cor_p_1.column.isin(list(genus_t.columns))]

    # only keep r >= 0.8 and p-value< 0.01
    cor_p_3 = cor_p_2[(abs(cor_p_2.cor) >= 0.8) & (cor_p_2.p < 0.01)]
    # save as csv file
    cor_p_3.to_csv('correlation.csv', sep='\t', index=False)
    # change to 2D dataset
    cor_p_3_2D = cor_p_3.pivot(index='row', columns='column', values='cor')
    # plot and save image
    cor_fig = sns.heatmap(cor_p_3_2D, vmin=0.8, vmax=1, cmap="crest", xticklabels=True, yticklabels=True)

    cor_fig.get_figure().savefig('cor_fig.png', dpi=300, bbox_inches='tight')

    print(colored("Correlation analysis was completed", 'red'))
    print('----------------------------------')


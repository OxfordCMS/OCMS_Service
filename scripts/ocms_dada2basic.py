'''
cms_basic.py
=============

:Author: Nick Ilott
:Tags: Python

Purpose
-------

.. Overall purpose and function of the script>

Takes directories of where basic OCMS data analyses were performed and creates a new directory that contains output files that are to
be transferred to the customer.

Files that are provided are:

Fastqc report (html)
dada2 report (html)
taxa_abundances.tsv (ASV level count data)
species_abundance.tsv (count data at species level)
genus_abundance.tsv (count data at genus level)
family_abundance.tsv (count data at family level)
order_abundance.tsv (count data at order level)
class_abundance.tsv (count data at class level)
phylum_abundance.tsv (count data at phylum level)


Usage
-----

.. Example use case

Example::

   python cms_basic.py --dada2-dir=<path-to-dada2-run> --fastqc-dir=<path-to-fastqc-run> --project-name=<name-of-project>

Type::

   python sdrf2map.py --help

for command line help.

Command line options
--------------------

'''

import sys
import os
import cgatcore.experiment as E
import glob
from datetime import datetime

def buildFileDescription(project_name):
    '''
    build a file description file
    '''
    file_layout=f"""
    Directory structure
    --------------------

    |-{project_name}
    |---Files.txt
    |------Reports
    |---------analysis_report.html
    |---------dada2_report.html
    |------Data
    |---------abundance_table.tsv
    |---------merged_table.tsv
    |---------taxonomy_table.tsv

    Description
    ------------

    analysis_report.html -> Summary of the analysis performed, with feedback from OCMS
    dada2_report.html -> Metrics on the dada2 run including reads input and output and taxonomic assignments.
    abundance_table.tsv -> Read counts for each amplicon sequence variant (ASV)(rows) detected per sample (columns).
    taxonomy_table.tsv -> Sequence and taxonomic classification assigned to each ASV
    merged_table.tsv -> Merge of abundance and taxonomy table, while dropping sequence and ASV identifiers.

    """
    with open(f"{project_name}/Files.txt", "w") as outf:
        # write text
        outf.write(file_layout)

        # add date created
        stat = datetime.today().strftime('%d-%m-%Y')
        outf.write("file created: ")
        outf.write(stat)

############################################
############################################
############################################
    
def main(argv=None):
    """script main.
    parses command line options in sys.argv, unless *argv* is given.
    """

    if argv is None:
        argv = sys.argv

    # setup command line parser
    parser = E.OptionParser(version="%prog version: $Id$",
                            usage=globals()["__doc__"])

    parser.add_option("--dada2-dir", dest="dada2_dir", type="string",
                      help="supply dada2 run directory")
    parser.add_option("--report-file", dest="report_file", type="string",
                      help="supply analysis report file")
    parser.add_option("--project-name", dest="project_name", type="string",
                      help="project name used to create master directory")

    
    # add common options (-h/--help, ...) and parse command line
    (options, args) = E.start(parser, argv=argv)

    dada2_dir = options.dada2_dir
    project_name = options.project_name
    report_file = options.report_file
    current_date = datetime.today().strftime('%d-%m-%Y')
    
    # make directories
    os.system(f"mkdir {project_name}; mkdir {project_name}/Reports; mkdir {project_name}/Data")

    # get all of the dada2 data
    dada2_data = [os.path.join(dada2_dir, "abundance.dir/taxa_abundances.tsv"), os.path.join(dada2_dir, "abundance.dir/merged_abundance_id.tsv")] 
    dada2_data = dada2_data + glob.glob(os.path.join(dada2_dir, "taxonomy.dir/merged_taxonomy.tsv"))
    dada2_data = " ".join(dada2_data)
    dada2_report = os.path.join(dada2_dir, "report.dir/report.html")
    
    # do the copying and renaming
    os.system(f"cp {dada2_data} {project_name}/Data; cp {dada2_report} {project_name}/Reports; cp {report_file} {project_name}/Reports; mv {project_name}/Reports/report.html {project_name}/Reports/dada2_report.html; mv {project_name}/Data/taxa_abundances.tsv {project_name}/Data/merged_table.tsv; mv {project_name}/Data/merged_abundance_id.tsv {project_name}/Data/abundance_table.tsv; mv {project_name}/Data/merged_taxonomy.tsv {project_name}/Data/taxonomy_table.tsv")

    # build file description
    buildFileDescription(project_name)

    # compress export folder
    os.system(f"tar -czf {project_name}_{current_date}.tar.gz {project_name}")

    # write footer and output benchmark information.
    E.stop()

if __name__ == "__main__":
    sys.exit(main(sys.argv))

================================================================
VCF2NETWORKS
================================================================


VCF2Networks is a python script that allows to calculate Genotype Networks from a Variant Call Format (VCF) file.

Genotype Networks are a method used in the field of Systems Biology to study the "Evolvability" or the "Innovability" of a genetic system. They have been applied to a wide range of systems, like genetic circuits ([1]_, [2]_, [3]_)⁠⁠, metabolic networks [4]_, [5]_, [6]_, [7]_, [8]_), and RNA and protein foldings ([9]_, [10]_)⁠. In recent times, they have also been used to reconcile the neutralist and selectionist views on evolution ([11]_)⁠, and to examine exaptation in metabolic networks ([12]_)⁠. 

This library allows to apply genotype networks to Single Nucleotide Polimorphism data, thus studying these networks at the level of population genetics, or in case-control studies.



INSTALLING
++++++++++

VCF2Networks is a suite of python scripts that run on the terminal. At the moment, there is no graphical interface, and only UNIX systems are supported.

The recommended way to install VCF2Networks is to use easy_install or pip, installing it from the Python Package Index (PyPI):

::

    $: easy_install vcf2networks

If the above command does not work, or if for whatever reason you are not able
to install VCF2Networks, please consult the detailed `Install Instructions`_. In
particular, VCF2Networks is based on the python-igraph>0.6 package, which at the
moment is not fully supported in PyPI, and must be installed manually. See the
instructions for more details.


BASIC TUTORIAL
++++++++++++++


VCF2Networks allows to parse a VCF file, and produce a tabular report of the Genotype Network properties of the file. 

Here is a short tutorial on how to run it on a sample VCF file, exploring the most important options.


Datafiles to follow this tutorial
---------------------------------

This tutorial contains some examples, based on a sample VCF file and some parameters. To follow the tutorial, please download the example files from here:
tutorial_data.zip_, and decompress them to your working directory.


Checking if VCF2Networks is installed
-------------------------------------

The main script in VCF2Networks is called vcf2networks. If you installed
VCF2Networks succesfully, this script should be installed in your PATH folder.
To check if vcf2networks is installed, type:

:: 
    
    $: vcf2networks --help

You should get a summary of all the options available for the script.


Simple example
----------------

The following example shows the basic usage of VCF2Networks:

::

    $: vcf2networks  --vcf tutorial/MOGS.recode.vcf --individuals_file tutorial/individuals_annotations.txt
    file_prefix continent   n_datapoints    n_components    av_path_length  av_degree   window      whole_gene_nsnps
    MOGS        glob        2184            17              3.847           2.5037      window_0    37
    MOGS        EUR         758             7               2.6508          2.3256      window_0    37
    MOGS        ASN         572             6               2.9             2.0         window_0    37
    MOGS        AMR         362             8               2.6477          2.1277      window_0    37
    MOGS        AFR         492             15              3.4103          2.0         window_0    37

This command will calculate the properties of the Genotype Network of the file "MOGS.recode.vcf". The first line of the output (after the headers) will show the properties of the network built using all the individuals in the file. The next lines give details of the networks built for each population separately. 
   
Each line contains some information about the Genotype Networks of a population. The first three columns give details about the file name, the population, and the number of haplotypes for each population. The fourth, fifth and sixth columns show the Number of Components, Average Path Length and the Average Degree respectively. It seems that for this region, African populations have an high number of components (15), while Europeans and Americans have a very low average path length (2.6508 and 2.6477).

The last two columns contain debugging information, like a unique id for each network, and the total of SNPs available.

(note: the actual output may different from the one shown. In particular, fields will be separated by a space, instead of tabulation. Open the output in a spreadsheet to see it better.)



Let's have a look at the options
--------------------------------

Let's have a look at the options used in the previous example.


--vcf tutorial/MOGS.recode.vcf:        
    The --vcf option is used to indicate which VCF file must be parsed to generate the networks. The VCF file must be sorted by position, and contain only diploid individuals. At the moment only Single Nucleotide Polimorphism data is supported, so you must remove any other type of variation before using the file.


--individuals_file tutorial/individuals_annotations.txt:
    The --individuals_file option points to the file containig the list of individuals, and their annotations. This file also contains any information on the phenotype of the individuals. Have a look at the file data/individuals/individuals_annotations.txt for an example.


Another useful option is --config, which describes a parameters file containing the network properties that have to be calculated.

--config tutorial/simple_params.yaml:                           
    The --config option is used to point to a configuration file, containing the list of the Genotype Network properties to be calculated. Have a look at the file params/simple.yaml to have an idea of which properties can be included in the output file.



The config file: let's add new Network Properties to the output
------------------------------------------------------------------------

If you look at the tutorial/simple_params.yaml file, you will see that there are a lot of properties that can be printed, apart from the ones in the first example.


Here are the contents of the tutorial/simple_params.yaml file:


::

    $: cat tutorial/simple_params.yaml

    # Properties to be included in the report of the network properties
    networkproperties_report_fields:
    #    - gene
        - file_prefix
    #    - distance_definition
        - n_snps
        - central_snp
        - chromosome
        - central_snp_position
    #    - upstream_position
    #    - downstream_position
        - region_size  # size of the window, in nucleotides pairs
    #    - distance_from_upstream_margin
    #    - distance_from_downstream_margin
        - n_datapoints
        - av_datapoints_per_node
        - n_vertices
        - n_edges
        - n_components
        - av_path_length
    #    - var_path_length
        - diameter
        - av_w_path_length
    #    - av_w_path_length_inv
        - av_degree
    #    - var_degree
    #    - median_degree
        - max_degree
        - av_w_degree
    #    - av_w_degree_inv

As you can see, there is a long list of network properties, the majority of which is uncommented. 

Uncomment any of these network properties to include it in the output report, and then run the script using the --config option:

::

    $: vcf2networks  --vcf tutorial/MOGS.recode.vcf --config tutorial/simple_config.yaml --individuals_file tutorial/individuals_annotations.txt
    file_prefix continent   distance_definition n_snps  central_snp     region_size n_datapoints n_components   av_path_length  diameter    av_closeness max_closeness  av_betweenness  window  whole_gene_nsnps
    MOGS        glob        1                   37      rs188042257     23805       2184            17          3.847           10          0.011       0.0132          57.6148         window_0    37
    MOGS        EUR         1                   37      rs188042257     23805       758             7           2.6508          5           0.0414      0.0517          14.5116         window_0    37
    MOGS        ASN         1                   37      rs188042257     23805       572             6           2.9             7           0.0514      0.064           11.2812         window_0    37
    MOGS        AMR         1                   37      rs188042257     23805       362             8           2.6477          6           0.0292      0.0354          9.8511          window_0    37
    MOGS        AFR         1                   37      rs188042257     23805       492             15          3.4103          8           0.0194      0.0252          21.726          window_0    37


A detailed description of all the columns available for VCF2Network is provided in the Supplementary Materials 1 of the paper (this part of the documentation will be updated after publication).


Grouping individuals by phenotype, instead of populations
----------------------------------------------------------

Another useful option in VCF2Network is to generate networks using information on the phenotype, instead that by population. For example, you can create two networks for the "Tall" and the "Short" individuals, and see if they have different properties. 

To produce networks based on phenotype, you must first be sure that the "individuals" file contains a column for the phenotype. For example, have a look at the individuals file provided in this repository:

::
    
    $: cat tutorial/individuals_file.txt

    #ID         POP     CONTINENT        PHENOTYPE1
    HG00096	GBR	EUR	        disease
    HG00097	GBR	EUR	        control
    HG00099	GBR	EUR	        control
    HG00100	GBR	EUR	        disease
    HG00101	GBR	EUR	        control
    HG00102	GBR	EUR	        control
    HG00103	GBR	EUR	        disease
    HG00104	GBR	EUR	        control
    HG00106	GBR	EUR	        control
    HG00108	GBR	EUR	        disease
    HG00109	GBR	EUR	        control
    HG00110	GBR	EUR	        control
    HG00111	GBR	EUR	        disease
    HG00112	GBR	EUR	        control
    HG00113	GBR	EUR	        control
    HG00114	GBR	EUR	        disease
    HG00116	GBR	EUR	        disease
    HG00117	GBR	EUR	        disease
    HG00118	GBR	EUR	        control
    HG00119	GBR	EUR	        disease
     
The fourth column in this file contains a phenotype called "PHENOTYPE1", which classifies individuals into "disease" and "controls". 

Let's use the --phenotype option to see if these two sets of individuals have different properties:

::

    $: vcf2networks  -g tutorial/MOGS.recode.vcf -c tutorial/simple_config.yaml -i tutorial/individuals_annotations.txt --phenotype PHENOTYPE1
    file_prefix PHENOTYPE1  n_components    av_path_length  av_degree   window      whole_gene_nsnps
    MOGS        glob        17              3.847           2.5037      window_0    37
    MOGS        disease     14              3.5768          2.1667      window_0    37
    MOGS        control     15              3.8127          2.3148      window_0    37

Well, it seems that the "disease" individuals have a lower average degree than the control one (2.1667 agains 2.3148), although overall, the differences are not very big in this disease.



Subsampling individuals
-----------------------

When the dataset in your VCF file contains a different number of individuals for each population (phenotype group), it is useful to sample only a fixed number of individuals for each population. This can be done using the --sample option. The following example samples only 500 haplotypes for each group:

::

    $: vcf2networks --sample 500 --vcf tutorial/MOGS.recode.vcf --config tutorial/simple_config.yaml -p PHENOTYPE1 
    file_prefix PHENOTYPE1  n_datapoints    n_components    av_path_length  av_degree   window      whole_gene_nsnps
    MOGS        glob        2184            17              3.847           2.5037      window_0    37
    MOGS        global_sub  500             12              3.3886          1.9697      window_0    37
    MOGS        disease     500             12              3.3939          1.8113      window_0    37
    MOGS        control     500             16              3.6625          2.2105      window_0    37

The first line of the output shows the values for the global population, using all the individuals. The second line shows the values of t


Applying a sliding window approach
----------------------------------

An useful option in vcf2networks is -w, which allows to apply a sliding windows
approach. 


::

    $: python src/vcf2networks.py  -g data/vcf_filtered/MOGS.recode.vcf -c params/default.yaml     -w 12 -p PHENOTYPE1
    file_prefix PHENOTYPE1 n_snps central_snp chromosome central_snp_position region_size n_datapoints av_datapoints_per_node n_vertices n_edges n_components av_path_length diameter av_w_path_length av_degree max_degree av_w_degree av_closeness max_closeness max_betweenness window whole_gene_nsnps
    MOGS glob 12 rs73949668 2 74681774 8871 2184 80.8889 27 35 1 3.8063 9 0.4238 2.5926 10 0.2244 0.2736 0.3662 168.2455 window_0 37
    MOGS pink 12 rs73949668 2 74681774 8871 1508 62.8333 24 31 1 3.5471 8 0.5224 2.5833 10 0.2383 0.2949 0.4035 150.8242 window_0 37
    MOGS blue 12 rs73949668 2 74681774 8871 676 32.1905 21 23 1 3.7905 9 0.6178 2.1905 8 0.1984 0.2785 0.3922 123.4333 window_0 37
    MOGS glob 12 rs184552219 2 74690931 8383 2184 84.0 26 29 3 2.6346 6 0.3841 2.2308 7 0.2031 0.0713 0.0865 60.5 window_1 37
    MOGS pink 12 rs184552219 2 74690931 8383 1508 65.5652 23 26 2 2.4331 5 0.4191 2.2609 7 0.2342 0.0811 0.0957 49.3333 window_1 37
    MOGS blue 12 rs184552219 2 74690931 8383 676 28.1667 24 26 3 2.5188 6 0.4074 2.1667 7 0.2051 0.0778 0.0954 55.0 window_1 37
    MOGS glob 12 rs139210283 2 74698509 5737 2184 66.1818 33 48 1 3.178 7 0.1858 2.9091 8 0.1363 0.3246 0.4923 234.2405 window_2 37
    MOGS pink 12 rs139210283 2 74698509 5737 1508 68.5455 22 27 1 2.9567 5 0.2262 2.4545 6 0.1712 0.3494 0.5385 123.8667 window_2 37
    MOGS blue 12 rs139210283 2 74698509 5737 676 23.3103 29 40 1 3.1133 7 0.1921 2.7586 8 0.1229 0.3324 0.5 189.9 window_2 37

As you can see, the data in the file MOGS.recode.vcf, which contains 37 SNPs, is splitted into windows of 12 SNPs (the remaining SNP is ignored), and a different output is given for each region of 12 SNPs.

The sliding windows approach is useful to compare files that have a different number of SNPs. 

An useful option to be used with the sliding windows approach is the -l, which allows to do a sliding window approach using overlapping windows.



The GenotypeNetwork Class
+++++++++++++++++++++++++


Apart from the main vcf2networks script, there are many functions hidden in the
code of the library, which allow better performances, and customization.

For example, the file GenotypeNetwork.py contains the definition of the GenotypeNetwork
class, which can be used to calculate the network properties manually, or to
implement new functions. 

Basic usage of the Genotype Network class:

    Create an empty Genotype Network:
    >>> mynetwork = GenotypeNetwork(chromosome_len=3, name='mynetwork')

    Populate the graph from a set of genotypes:

    >>> genotypes = ['001', '010', '000']
    >>> mynetwork.populate_from_binary_strings(genotypes)
    
    # Print informations about the network:
    >>> print(mynetwork)
    Genotype Network (name = 'mynetwork', chromosome lenght = 3, \|V| = 3, \|E| = 2)

    >>> print(mynetwork.summary()) #doctest: +NORMALIZE_WHITESPACE
    3 nodes, 2 edges, undirected
    <BLANKLINE>
    Number of components: 1
    Diameter: 2
    Density: 0.6667
    Average path length: 1.3333

    # Print node degree distribution for the network
    >>> mynetwork.degree()
    [1, 1, 2]

    >>> print mynet.csv_report()
    mynet glob 3 5 5 3 2 2 0.3 1.0 1.5 1.2 3 0.6 0.38



Availability
------------

This repository is available at http://bitbucket.org/dalloliogm/vcf2networks/overview


Project outline, TO-DO list and bugs
------------------------------------

Project Proposal and TO-DO lists are implemented in separate trello boards. 

- Project Proposal board: https://trello.com/b/HxRUQmaM

- TO-DO list and tasks: https://trello.com/b/ehNHtM3S
 
Bugs are usually posted to the TO-DO trello board, in one of the TO-DO columns. 


REFERENCES
++++++++++

.. _tutorial_data.zip: http://bioevo.upf.edu/~gdallolio/vcf2networks/tutorial.zip
.. _Install Instructions: https://bitbucket.org/dalloliogm/vcf2networks/src/tip/docs/installing.rst
.. _source: https://bitbucket.org/dalloliogm/vcf2networks/get/tip.zip
.. [1] Wagner, 2003: Does selection mold molecular networks? 2003, PE41.
.. [2] Espinosa-Soto et al., 2011: Phenotypic plasticity can facilitate adaptive evolution in gene regulatory circuits. BMC Evol. Biol., 11, 5.
.. [3] Ciliberti et al., 2007: Innovation and robustness in complex regulatory gene networks. Proc. Natl. Acad. Sci. U. S. A., 104, 13591–6.
.. [4] Wagner, 2009: Evolutionary constraints permeate large metabolic networks. BMC Evol. Biol., 9, 231.
.. [5] Wagner, 2007: From bit to it: how a complex metabolic network transforms information into living matter. BMC Syst. Biol., 1, 33.
.. [6] Matias Rodrigues and Wagner, 2009: Evolutionary plasticity and innovations in complex metabolic reaction networks. PLoS Comput. Biol., 5, e1000613.
.. [7] Samal et al., 2010: Genotype networks in metabolic reaction spaces. BMC Syst. Biol., 4, 30.
.. [8] Dhar et al., 2011: Adaptation of Saccharomyces cerevisiae to saline stress through laboratory evolution. J. Evol. Biol., 24, 1135–53.
.. [9] Ferrada and Wagner, 2010: Evolutionary innovations and the organization of protein functions in genotype space. PLoS One, 5, e14172.
.. [10] Schultes and Bartel, 2000: One sequence, two ribozymes: implications for the emergence of new ribozyme folds. Science, 289, 448–52.
.. [11] Wagner, 2008: Neutralism and selectionism: a network-based reconciliation. Nat. Rev. Genet., 9, 965–74.
.. [12] Barve and Wagner, 2013: A latent capacity for evolutionary innovation through exaptation in metabolic systems. Nature, 500, 203–6.


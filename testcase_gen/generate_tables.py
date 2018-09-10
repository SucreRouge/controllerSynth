__author__ = 'rajesh kedia'

'''
<Embedded System Design>
This program generates tables for use in the runtime controller specification optimization.

Written By: Rajesh Kedia
Organization: IIT Delhi
Last Edit : September 9, 2018


the format for the configuration file is as follows:
        <num_of_tables>
        <num_of_variables_min> <num_of_variables_max>
        <num_of_modes_min> <num_of_modes_max>
        <value_count_min> <value_count_max>
        <type_of_table> : enumerated - 1: low merging, 2: medium merging, 3: high merging possible
        <num_of_entries_max_limit> : specify a number or 0 if no limit

Following is the algorithm followed for this:
        1. generate all combinations of different variables and store them in a list. we use itertools to accomplish the same. the combinations are stored in lexicographic order in the list.
           This helps to ensure that the same entry is not repeated in the table, and also simplifies control of the merging capability.
        2. based on the type of table needed, the mode assignment is done. Same mode is assigned for continuous items from the list if higher merging is chosen
        3. We generate 95% of entries as per the merging level, while remaining 5% are completely random generated
'''

import sys
import math
import os
import random
import itertools

##class to contain various configuration settings, parsed from the file
class Config:
    num_of_tables = 0           ## total number of tables to be generated
    num_of_var_min = 0          ## minimum number of variables to be considered
    num_of_var_max = 0          ## maximum number of variables to be considered (the actual number is a random number between minimum and maximum)
    num_of_modes_min = 0        ## minimum number of modes to be generated
    num_of_modes_max = 0        ## maximum number of modes to be generated (actual number is a random number between minimum and maximum)
    value_count_min = 0         ## minimum number of values for each variable
    value_count_max = 0         ## maximum number of values for each variable
    type_of_table = 0           ## type of table - enumerated as 1, 2, 3
    num_of_entries_max = 0      ## maximum number of entries. the actual number is a minimum of this or the maximum possible entries, as per randomly chosen variables, etc.

## procedure to parse the config file and update the class Config based on the same
def parse_config_file(file_name):
    fp = open(file_name, "r")
    contents = fp.read()
    contents = contents.split("\n")
    if contents[-1] == '':
        contents.pop()

    cfg = Config()
    cfg.num_of_tables = int(contents[0])
    t = contents[1].split()
    cfg.num_of_var_min = int(t[0])
    cfg.num_of_var_max = int(t[1])
    t = contents[2].split()
    cfg.num_of_modes_min = int(t[0])
    cfg.num_of_modes_max = int(t[1])
    t = contents[3].split()
    cfg.value_count_min = int(t[0])
    cfg.value_count_max = int(t[1])
    cfg.type_of_table = int(contents[4])
    cfg.num_of_entries_max = int(contents[5])
    fp.close()
    return cfg

## generate a random number between minimum and maximum
def generate_random(minimum, maximum):
    return random.randint(minimum, maximum)

## generate a random number between minimum and maximum
def generate_all_combinations(num_var, var_list):
    prod = ()
    l = list(prod)
    for i in range(num_var):
        var_values = range(var_list[i])     ## var_list contains the maximum value for each variable
        l.append(var_values)        ## l contains the different values for each variable
    prod = tuple(l)
    product_list = itertools.product(*prod, repeat=1)       ## use itertools to generate all combinations of the variables
    complete_list = []
    for l in product_list:
        ljoined = ",".join(str(w) for w in l)               ## add comma in between each variable of the list to match the required format for output
        complete_list.append(ljoined)                       
    return complete_list                                    ## return the list containing all combinations of the variables

## generate one table based on selected configuration
def generate_one_table(file_name, cfg):
    var_limits = []
    num_var = generate_random(cfg.num_of_var_min, cfg.num_of_var_max)               ## generate number of variables
    num_modes = generate_random(cfg.num_of_modes_min, cfg.num_of_modes_max)         ## number of modes

    fout = open(file_name, "w+")
    fout.write(str(num_var)+"\n")
    fout.write(str(num_modes)+"\n")

    valid_combinations = 1                                              ## refers to the count of valid combinations as per randomly generated num_var, num_modes and value counts
    for i in range(num_var):
        lim = generate_random(cfg.value_count_min, cfg.value_count_max)
        var_limits.append(lim)
        s = "0 " + str(lim) + " 1\n"                                ## defaulting the step count for each variable to 1. can be made real number to allow finer ranges
        fout.write(s)
        valid_combinations *= (lim)                                 ## multiply the maximum value for calculating the total valid combinations
    print valid_combinations
    table_entries = min(cfg.num_of_entries_max, valid_combinations)     ## total number of entries is the minimum of valid combinations, or the limit in the config file
    total_structured_entries = int(0.95*table_entries)                  ## 95% entries are generated as per the merging level, 5% are completely random
    total_random_entries = table_entries - total_structured_entries
    print total_structured_entries, total_random_entries

    complete_list = generate_all_combinations(num_var, var_limits)      
    list_index = 0
    str_entry_count = 0
## generate the table based on type of table. if low merging, less number of continuous modes are assigned to the sorted list of combinations
    while str_entry_count < total_structured_entries:
            ##random count within a range, depending upon the merging level. this count denotes how many continuous entries are assigned the same mode.
            ## the range of values for random number are empirically assigned.
        if cfg.type_of_table == 1:
            mode = generate_random(0, num_modes-1)
            group_length = generate_random(1,3)
        elif cfg.type_of_table == 2:
            mode = generate_random(0, num_modes-1)
            group_length = generate_random(6,9)
        elif cfg.type_of_table == 3:
            mode = generate_random(0, num_modes-1)
            group_length = generate_random(18,22)
            ## based on the count, assign the mode to the continuous minterms in the complete list
        for i in range(group_length):
            l = complete_list[list_index]
            lj = l + ":" + str(mode) + "\n"
            str_entry_count += 1
            list_index += 1
            fout.write(lj)
            if str_entry_count == total_structured_entries:
                break

    ## generate the table for 5% of completely random combinations
    random_entry_count = 0
    while random_entry_count < total_random_entries:
        mode = generate_random(0, num_modes-1)
        l = complete_list[list_index]
        lj = l + ":" + str(mode) + "\n"
        random_entry_count += 1
        list_index += 1
        fout.write(lj)
    fout.close()

## this function assigns file name for generating multiple unique tables.
## based on specified output file name, the suffix _num is assigned, starting from 0.
## e.g. if user specifies out.txt as output file and 3 tables are to be generated, they will be named out_0.txt, out_1.txt, out_2.txt.
def get_file_name(out_file, count):
    if "." in out_file:
        strings = out_file.split(".")
        name = strings[0]
        extension = "."+strings[1]
    else:
        name = out_file
        extension = ""
    name = name+"_"+str(count)+extension
    return name


## main function.
## takes arguments from the command line and passes to different function.
def main():
    arguments = sys.argv[1:]
    ## error out if wrong usage on the command line
    if len(arguments) < 2:
        print "\nError: the expected usage is:\n"
        print "python generate_tables_linear_controlled_compression.py <cfg file name> <output file name>\n"
        print "example: python generate_tables_linear_controlled_compression.py gen_table.cfg table.txt\n"
        return

    print "Runtime controller generation for CAES"
    print "Generate random tables for different scenarios"
    in_file = arguments[0]
    out_file = arguments[1]
    cfg = Config()                  ## create the cfg instance of Config class containing values from the file.
    cfg = parse_config_file(in_file)        ## assign values to cfg
#    print cfg.num_of_tables,  cfg.num_of_var_min,  cfg.num_of_var_max, cfg.num_of_modes_min , cfg.num_of_modes_max,  cfg.type_of_table, cfg.num_of_entries_max 
    for count in range (cfg.num_of_tables):     ## repeat the loop for the number of tables required to be generated
        out_file_name = get_file_name(out_file, count)  ## generate file name as per the iteration count
        generate_one_table(out_file_name, cfg)          ## generate one table for the particular file name

if __name__ == "__main__":
    main()

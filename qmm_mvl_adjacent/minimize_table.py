__author__ = 'rajesh kedia'

'''
<Embedded System Design>
This program reads the table entries for runtime controller and generates a minimized table by merging adjacent rows.
This program uses a modified version of Quine Mccluskey method, extended to multi-valued logic.

The input table is assumed to be enumerated with ranges converted to different integers, starting from 0.
Pending: To use the range and generate the enumeration on its own.

The code invokes the QMM (Quine Mc-Cluskey method for each of the modes separately and writes to the file each time for every mode.
To invoke QMM, it generates a temp.txt in the format needed by QMM by parsing the entries from the input table.
This is found efficient compared to doing it for all modes together.

Written By: Rajesh Kedia
Last Edit : Sep. 9, 2018

'''

import sys
import math
import os
import qm_userInputFile as qm

## this function appends the mode information to the reduced implicants obtained from QM method
## for the input table, it appends the mode in specified format and returns the updated list.
def append_mode(reduced_table, mode):
    updated = []
    for i in range(len(reduced_table)):
        updated.append(reduced_table[i][0]+":"+str(mode))
    return updated

## this function converts the table entries into a map where we maintain list of minterms for each mode separately
def table_to_map(file_name):
    fp = open(file_name, "r")
    if fp.mode == "r":
        print "file opened"

    contents = fp.read()
    contents = contents.split("\n")
    num_var = int(contents[0])
    num_modes = int(contents[1])
    ## the map to store the minterms for each mode. It is a 2-D list.
    maps = [[] for x in range(num_modes)]
    value_count = [[] for x in range(num_var)]          ## based on specified min, max. and the step size, the number of distinct range is computed and assigned to value_count.
    contents = contents[2:]                     # skip the first 2 rows which were headers for num_var and num_modes
    ## reading the variable settings and updating the value_count list with count for each of them.
    for i in range(num_var):
        line = contents[i]
        line = line.split()
        t0 = float(line[0])                  #format is start end stepsize
        t1 = float(line[1])
        t2 = float(line[2])
        count = (t1-t0)/t2
        count -= 1
        count = int(math.ceil(count))       ##find the total number of steps for the particular variable
        value_count[i] = count

    contents = contents[num_var:]            ## now contents contain the table entries
    if contents[-1] == '':                   ## remove empty last element from the list
        contents.pop()
    initial_table_size = len(contents)      ## needed to compute the compression ratio
    ## read each line and add to appropriate mode in the list of list (maps).
    for i in range(len(contents)):
        line = contents[i].split(":")       ## the input file format is minterm:mode for each entry, in a separate line
        minterm = line[0]           
        mode = int(line[1])
        maps[mode].append(minterm)          ## add to list corresponding to the mode
    fp.close()
    return maps, num_var, value_count, initial_table_size   #return the mapped structure, the number of variables and the value count for each of them.

## this function minimize the table using the QMM method
## the QM function present in another file is called here and the result is parsed to generate back the table
## the QM is invoked separately for all minterms of one mode and then repeated for each of the modes
def minimize_using_qm(maps, out_file, num_var, value_count):
    fout = open(out_file, "w+")         #file pointer to store the output
    final_table_size = 0                ## used to store the final size, needed to compute the compression

    for j in range(len(maps)):          #run for each mode
        mapj = maps[j]
        fp = open("temp.txt", "w+")     #temporary file to pass arguments to the QMM function
        fp.write(str(num_var)+"\n")
        ## format as per expected format for QMM. Add value count for each variable in a space separated format.
        for i in range(len(value_count)):
            fp.write(str(value_count[i]) + " ")

        fp.write("\n")
        ## write each of the minterm from the table into the QMM in the expected format, minterms separated by space
        for i in range(len(mapj)):
            fp.write(mapj[i]+" ")
        fp.close()                      #end of generation of input file for QM function

        ## now do the minimization. invoke QMM for each mode separately.
        if len(mapj) != 0:
            x=qm.quine_mccluskey("temp.txt")        # invoke QM with the generated file as input
            x=append_mode(x,j)                      # update the output of QM with mode information
            final_table_size += len(x)
            ## write the minimized form to the output file
            for entry in x:
                fout.write(entry + "\n")            #add in the output file
    fout.close()
    os.system("rm temp.txt")
    return final_table_size

## the main function.
## reads the command line arguments and invokes the function to perform the required computations
def main():
    arguments = sys.argv[1:]
    ## error out if wrong usage on the command line
    if len(arguments) < 2:
        print "\nError: the expected usage is:\n"
        print "python minimize_table.py <input table file> <output file name>\n"
        print "example: python minimize_table.py table_0.txt minimized.txt\n"
        return
    print "Runtime controller generation for CAES"
    print "Minimizing the tables to merge adjacent rows"

    in_file = arguments[0]
    out_file = arguments[1]

    ## convert the table to a local data structure named maps.
    maps, num_var, value_count, initial_table_size = table_to_map(in_file)

    ## invoke the minimize function using the information parsed from the file.
    final_table_size = minimize_using_qm(maps, out_file, num_var, value_count)

    print "initial table size =", initial_table_size, "final_table_size=", final_table_size

if __name__ == "__main__":
    main()

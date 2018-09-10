__author__ = 'rajesh kedia'

'''
<Logic Design>
This is a program that implements Quine-McCluskey Method. It works for multi-valued logic and can be used to merge adjacent minterms.
It is developed in a context to minimize controller specifications for embedded systems.

Author: Rajesh Kedia
Last change : Sep 9, 2018
Acknowledgement: Initial code borrowed from: JongHewk Park (https://github.com/jonghewk/Quine_McCluskey)

Here is the algorithm
1. Find the prime implicants
2. Make Prime implicant chart
3. Find essential prime implicants
4. Use Petrick's Method to find all solutions

This file was modified by Rajesh Kedia in August 2018 to extend the implementation to support
any arbitrary number of variables, each in decimal number system with different number of values for 
each of them.

'''


import itertools
import sys
import logging
import copy

#compare two binary strings, check where there is one difference
#RK: updated the function to compare when the term contains merged range, and also to enable merging if merging is possible
# this function returns True if there is a merging, along with the position of merging, along with the starting and ending value of the merged range
def compareItems(s1,s2):
    count = 0
    pos = 0
    for i in range(len(s1)):
        ## do nothing if the same portion within the minterm
        if (s1[i] != s2[i]):
            count+=1
            ## check if already a merged range (presence of '-') in s1
            if ('-' in s1[i]):  #extract 2 portion of the range for s1
                t1 = s1[i].split('-')
                t10 = int(t1[0])
                t11 = int(t1[1])
            else:               #if it is single value, assign it to both of the variables
                t10 = int(s1[i])
                t11 = int(s1[i])

            ## check if already a merged range (presence of '-') in s1
            if ('-' in s2[i]):  #extract 2 portion of the range for s2
                t2 = s2[i].split('-')
                t20 = int(t2[0])
                t21 = int(t2[1])
            else:
                t20 = int(s2[i])
                t21 = int(s2[i])

            #if difference is 1, it means they are just single values. merge them to create a range for next group
            if (t20-t11 == 1 and t10==t11):
                r1 = str(t11)
                r2 = str(t20)
                pos = i

            #if there is an overlap in the two ends, it means that there is a range being merged with another range.
            #using >= sign in the next check as 9-11 and 10-12 needs to be merged to 9-12
            elif (t11 >= t20):    
                r1 = str(t10)
                r2 = str(t21)
                pos = i
            elif (t21 >= t10):
                r1 = str(t20)
                r2 = str(t11)
                pos = i
            else:
                count+=1         ##increase count again if merging condition is not satisfied to create error (count=1 is only recognized valid)
    if count == 1:
        return True, pos, r1, r2        #return the two ends of range along with other information
    else:
        return False, None, None, None


#s1 should be the term
#RK: updated the function to compare if a minterm is covered in the implicant or not
def compBinarySame(implicant, minterm):
    minterm = minterm.split(",")
    implicant = implicant[0].split(",")
    ## check that all portion are either same or covered within the implicant range
    for i in range(len(implicant)):
        if implicant[i] != minterm[i]:
            if ('-' in implicant[i]):  #extract 2 portion of the range for term
                t2 = implicant[i].split('-')
                t20 = int(t2[0])
                t21 = int(t2[1])
                if not((int(minterm[i]) >= t20) and (int(minterm[i]) <= t21)):
                    return False
            else:
                return False
    return True         ## True indicates if the minterm is covered in the implicant


#combine pairs and make new group
#RK: updated the function to take the values returned by the compareItems function and use to create the new term.
## if the minterms are adjacent, then they are combined to make an implicant
def combinePairs(group, unchecked):
    #define length
    l = len(group) -1

    #check list
    check_list = []

    #create next group to store the merged ranges
    next_group = [[] for x in range(l)]

    #go through the groups
    for i in range(l):
        #first selected group
        for elem1 in group[i]:
            #next selected group
            elem1 = elem1.split(",")
            for elem2 in group[i+1]:        ## compare with adjacent groups only
                elem2 = elem2.split(",")
                b, pos, t1, t2 = compareItems(elem1, elem2)     ## get the comparison result from the function
                if b == True:           ## if merging is possible
                    #append the ones used in check list, so that they can be marked as covered
                    check_list.append(",".join(elem1))
                    check_list.append(",".join(elem2))
                    #replace the different term with the values returned from the compareItems function
                    new_elem = list(elem1)          ##merged entry
                    new_elem[pos] = t1+'-'+t2
                    new_elem = ",".join(new_elem)
                    next_group[i].append(new_elem)      ## add to the new group

    # once all merging is done, keep the uncovered ones in the unchecked list as they are already Prime implicants
    for i in group:
        for j in i:
            j = j.split()
            if j[0] not in check_list:   ##using j[0] because j is a list of singleton string, we want to compare to string in the check_list
                unchecked.append(j)
    return next_group, unchecked        # return the merged group and the unchecked list


#remove redundant lists in 2d list
# it removes the duplicate entries from the group
def remove_redundant(group):
    new_group = []
    for j in group:
        new=[]
        for i in j:
            if i not in new:
                new.append(i)
        new_group.append(new)
    return new_group


#remove redundant in 1d list
# it removes the duplicate entries from the group
def remove_redundant_list(list):
    new_list = []
    for i in list:
        if i not in new_list:
            new_list.append(i)
    return new_list


#return True if a list is empty or contains only 0 as elements
def check_empty(group):

    if len(group) == 0:
        return True

    else:
        count = 0
        for i in group:
            if i:
                count+=1
        if count == 0:
            return True
    return False


#find essential prime implicants from the PI chart ( col num of ones = 1)
def find_prime(Chart):
    prime = []
    for col in range(len(Chart[0])):
        count = 0
        pos = 0
        for row in range(len(Chart)):
            #find essential
            if Chart[row][col] == 1:
                count += 1
                pos = row

        if count == 1:
            prime.append(pos)
    return prime

# check if all the minterms are covered in the essential PI, then no need of covering
def check_all_zero(Chart):
    for i in Chart:
        for j in i:
            if j != 0:
                return False        ## return false if any one of the entry is non-zero in the chart
    return True

#multiply two terms (ex. (p1 + p2)(p1+p4+p5) )..it returns the product
##RK: this function was modified to implement optimization of X=X+XY
## performs multiplication of different terms as used in petrick method
def multiplication(list1, list2):
    list_result = []
    #if empty
    if len(list1) == 0 and len(list2)== 0:          # return empty if both list are null
        return list_result

    # return the other list if any one is empty, but not the other
    #if one is empty
    elif len(list1)==0:
        return list2                
    #if another is empty
    elif len(list2)==0:
        return list1

    #perform multiplication if both are not empty
    else:
        logging.debug("Entering petrick multiplication loop")
        # iterate for each element in the list
        for i in list1:
            for j in list2:
                #if two term same
                #logging.debug(i)
                new_item_set = set(i+j)             ## create a set to contain the unique values within a term. e.g. P1P2 * P2P3 = P1P2P3 (P2 shouldn't come twice).
                new_item = list(new_item_set)       ## convert this set back to list
                list_result.append(new_item)

        #sort and remove redundant lists and return this list        
        # redundant items are:
        # repetition of the same term e.g. if P1P0 is coming twice, only one should be kept
        # if X+XY is there, then remove XY

        # below two steps perform the sorting and remove the duplicate entries from the list.
        list_result.sort()
        list_result = list(list_result for list_result,_ in itertools.groupby(list_result))

        ## create a copy of the original list, as original list is modified in the below steps and causes issues in the iterations
        ## however, terms which are in different order but redundant are removed in the next operation not here. e.g. P1P0 and P0P1 are same, but not removed here.
        list_result_copy = copy.copy(list_result)
        logging.debug(list_result_copy)

        # if X+XY is there, then remove XY. This operation is performed in below few lines
        for i1 in range(len(list_result_copy)):
            for i2 in range(len(list_result_copy)):         ## two loops compare each item in the list with another

                list_item1 = list_result_copy[i1]
                list_item2 = list_result_copy[i2]
                #print list_item1, list_item2

                # if one of them is a subset of another, then the larger one can be removed.
                if (set(list_item2) < set(list_item1)): 
                    list_result.remove(list_item1)
                    break
                # or if the two of them are the same but different ordering, remove one of them.
                elif (set(list_item2) == set(list_item1)) and (i1 != i2):
                    list_result.remove(list_item1)
                    break
        return list_result      # return the multiplied list

#petrick's method for finding the minimal cover
def petrick_method(Chart):
    logging.debug("Entering petrick method")
    #initial P
    P = []
    for col in range(len(Chart[0])):
        p =[]
        for row in range(len(Chart)):
            if Chart[row][col] == 1:
                p.append([row])
        P.append(p)             ## the initial P is the individual polynomial terms for each of the column

    logging.debug("printing P from petrick method")
    logging.debug(P)
    #do multiplication
    logging.debug("length of P array=%d" %len(P))
    ## iterate for each of the polynomial within P and perform multiplication

    for l in range(len(P)-1):
        logging.warn("Entering petrick multiplication method number: %d" %l)
        logging.warn(P[l+1])
        ## keep on doing multiplication for each of the terms (using left associativity rule)
        P[l+1] = multiplication(P[l],P[l+1])
        logging.warn("Size of P:%d" %len(P[l+1]))
        logging.debug(P[l+1])
        #aaa = raw_input("test")

    logging.debug("Completed petrick multiplication method")
    
## multiplication completed. Now sort them as per the number of terms within each of the term in the final polynomial
    logging.debug("Entering petrick sorting method")
    P = sorted(P[len(P)-1],key=len)
    final = []

    #find the terms with min length = this is the one with lowest cost (optimized result)
    min=len(P[0])           # minimum is the length of the first element in the sorted list

    ## now find all terms with the same length as the minimum. they are all valid minimal solutions
    for i in P:
        if len(i) == min:
            final.append(i)
        else:
            break
    #final is the result of petrick's method
    logging.debug("returning from petrick")
    return final            ## returns list of valid solutions

#chart = n*n list
def find_minimum_cost(Chart, unchecked):
    P_final = []
    #essential_prime = list with terms with only one 1 (Essential Prime Implicants)
    essential_prime = find_prime(Chart)
    essential_prime = remove_redundant_list(essential_prime)            # remove duplicates

    #print out the essential primes
    if len(essential_prime)>0:
        s = "\nEssential Prime Implicants :\n"
        print s
        for i in range(len(unchecked)):
            for j in essential_prime:
                if j == i:
                    print unchecked[i]

    #modifiy the chart to exclude the minterms covered by the essential primes
    for i in range(len(essential_prime)):
        for col in range(len(Chart[0])):
            if Chart[essential_prime[i]][col] == 1:
                for row in range(len(Chart)):
                    Chart[row][col] = 0

    logging.debug("Successful until chart generation for essential primes removal")

    #if all zero, no need for petrick method because all minterms are covered by essential primes
    if check_all_zero(Chart) == True:
        P_final = [essential_prime]
    else:
        #petrick's method
        P = petrick_method(Chart)           ## P is the set of all valid minimal solutions

        #find the one with minimum cost
        #see "Introduction to Logic Design" - Alan B.Marcovitz Example 4.6 pg 213
        '''
        Although Petrick's method gives the minimum terms that cover all,
        it does not mean that it is the solution for minimum cost!
        '''

        ## compute the cost of the solution. not relevant for the context of this work.
        P_cost = []
        for prime in P:
            count = 0
            for i in range(len(unchecked)):
                for j in prime:
                    if j == i:
                        count = count+ cal_efficient(unchecked[i])
            P_cost.append(count)


        ## find solution with minimal cost
        for i in range(len(P_cost)):
            if P_cost[i] == min(P_cost):
                P_final.append(P[i])

        #append essential prime implicants to the solution of Petrick's method
        for i in P_final:
            for j in essential_prime:
                if j not in i:
                    i.append(j)

    return P_final

#calculate the number of literals.
#This function is not correct, but not used in this context. Hence not updated.
#this is relevant when we want to count the number of terms in each implicant
def cal_efficient(s):
    count = 0
    for i in range(len(s)):
        if s[i] != '-':
            count+=1

    return count

#main function
##RK: modified to take input from file
##format: first line is number of variables
##        second line contains value count for each
##        third line contains all the minterms in the required format
## file name is specified as a command line argument by the invoker of the script

## performs the QMM minimization of the minterms from the file.
def quine_mccluskey(file_name):
    logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
    logging.debug('A debug message!')

    print "Reading file", file_name
    fp = open(file_name,"r")

    if fp.mode == 'r':
        file_contents = fp.read()
        file_contents = file_contents.split("\n")
        fp.close()

    ##RK: modified to take inputs about the value count for each variable and their minterms in comma separated format
    #get the num of variables (bits) as input
    n_var = int(file_contents[0])
    #get the size of each variable as input
    sizes = file_contents[1]

    s = sizes.split()           ## s contains the value count for each of the variable
    totalsize = 0
    if len(s) != n_var:
        print '\nError : Choose the correct number of entries in the value count\n'
        return
    for i in range(len(s)):
        totalsize = totalsize + int(s[i])           ## find the total size of the number of groups. this is the sum of value count for each variable

    #get the minterms as input
    ##RK: modified to take minterms input in comma separated format
    minterms = file_contents[2]                     ## specified in the input file, minterms separated by a space
    a = minterms.split()         #split on white space. list a contains the minterms separately

    #make a group list
    group = [[] for x in range(totalsize+1)]            ## create a list for each group in QMM separately

    ## iterate for each minterm, and assign it a group
    for i in range(len(a)):
        #convert to binary
        local_minterm = a[i].split(",")
        groupnum = 0
        ##RK: modified the error checking condition and message updated accordingly
        if len(local_minterm) != n_var:
            print '\nError : Choose the correct number of indices for the term number %d\n' % i
            return

        for j in range(len(local_minterm)):
            groupnum = groupnum + int(local_minterm[j])         ## find the sum of indices to determine the group number
            if (int(local_minterm[j])) > (int(s[j])):           ## check that the input is within the specified range
                print '\nError : Choose the correct value counts\n'
                return
        group[groupnum].append(a[i])                            ## append the minterm to the list of the corresponding group


    all_group=[]                ## contains the valid groups (non-empty) within the all_group.
    unchecked = []
    #combine the pairs in series until nothing new can be combined
    ##RK: no change to the toplevel functions, the internals of these function was changed

    #this function iteratively calls the combinePairs function until there is no merging possible.
    while check_empty(group) == False:
        all_group.append(group)
        next_group, unchecked = combinePairs(group,unchecked)           ## unchecked contains all the final implicants
        group = remove_redundant(next_group)

    ##RK: updated to print the prime implicants, one in each line instead of in a single line
    s = "\nPrime Implicants :\n"
    print s
    for i in unchecked:
        print i

    ## the step of creating the PI is over. Now, we create PI chart and process for minimal solution
    #make the prime implicant chart
    Chart = [[0 for x in range(len(a))] for x in range(len(unchecked))]

    ##RK: no change to the toplevel functions, the internals of these function was changed
    for i in range(len(a)):
        for j in range (len(unchecked)):
            #term is same as number
            if compBinarySame(unchecked[j], a[i]):
               Chart[j][i] = 1

    ## after creating the PI chart, invoke the minimization function which finds the essential primes and then invokes Petrick method for minimal cover
    primes = find_minimum_cost(Chart, unchecked)
    primes = remove_redundant(primes)

    print "\n--  Answers --\n"

##RK: this prints all possible optimal solutions. we are interested in only one solution, hence omitted for now.
#    for prime in primes:
#        s=''
#        for i in range(len(unchecked)):
#            for j in prime:
#                if j == i:
#                    print unchecked[i]      ##this is the prime implicant which is chosen to be in the final answer
#                    #s= s+binary_to_letter(unchecked[i])+' + '
#        print s[:(len(s)-3)]

    ##RK: this prints only the first valid solution
    ##RK: updated to print the prime implicants, one in each line instead of in a single line
    answer = []
    for i in range(len(unchecked)):
        for j in primes[0]:
            if j == i:
                print unchecked[i]      ##this is the prime implicant which is chosen to be in the final answer
                answer.append(unchecked[i])
    return answer


if __name__ == "__main__":
    arguments = sys.argv[1:]
    file_name = arguments[0]
    quine_mccluskey(file_name)

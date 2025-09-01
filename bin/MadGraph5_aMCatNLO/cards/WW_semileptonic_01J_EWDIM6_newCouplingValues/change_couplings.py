import os 
import sys

coupling_values = {
        '1' : 3.6,
        '2' : 4.5,
        '3' : 20.0,
        '4' : 9.999999e-01,
        '5' : 6.0
}



f = open('WWToLNuJJ_01j_LO_EWdim6NLO_reweight_card.dat', 'r')
contents = f.readlines()

new_f = open('out.dat', 'w')

for line in contents:
    if line.startswith('   set'): 
        print('if')
        l = line.split()
        if l[-1] == '0':
            pass
        elif l[-1] != '0':
            sign = float(l[-1])
            l[-1] = str(sign*coupling_values[l[-2]])


        l = "   " + " ".join(l) + "\n"
        new_f.write(l)
    else:
        print('else')
        new_f.write(line)

    print('-------')



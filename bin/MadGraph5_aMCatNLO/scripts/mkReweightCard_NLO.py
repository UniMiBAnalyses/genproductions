from itertools import combinations
import argparse
import os
import sys 

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-op","--op", help="Operator list to make the reweight card follwoing algebra" , nargs="+", required=True)
    parser.add_argument("-o", "--out", help="Out file name", required=True)
    args = parser.parse_args()


    smeftatnlo = {
        "DIM6": [
            [1, "Lambda"],
            [2, "cpDC"],
            [3, "cpWB"],
            [4, "cdp"],
            [5, "cp"],
            [6, "cWWW"],
            [7, "cG"],
            [8, "cpG"],
            [9, "cpW"],
            [10, "cpBB"]
        ],
        "DIM62F": [
            [1, "cpl1"],
            [2, "cpl2"],
            [3, "cpl3"],
            [4, "c3pl1"],
            [5, "c3pl2"],
            [6, "c3pl3"],
            [7, "cpe"],
            [8, "cpmu"],
            [9, "cpta"],
            [10, "cpqMi"],
            [11, "cpq3i"],
            [12, "cpQ3"],
            [13, "cpQM"],
            [14, "cpu"],
            [15, "cpt"],
            [16, "cpd"],
            [19, "ctp"],
            [22, "ctZ"],
            [23, "ctW"],
            [24, "ctG"]
        ],
        "DIM64F": [
            [1, "cQq83"],
            [2, "cQq81"],
            [3, "cQu8"],
            [4, "ctq8"],
            [6, "cQd8"],
            [7, "ctu8"],
            [8, "ctd8"],
            [10, "cQq13"],
            [11, "cQq11"],
            [12, "cQu1"],
            [13, "ctq1"],
            [14, "cQd1"],
            [16, "ctu1"],
            [17, "ctd1"],
            [19, "cQQ8"],
            [20, "cQQ1"],
            [21, "cQt1"],
            [23, "ctt1"],
            [25, "cQt8"]
        ],
        "DIM64F2L": [
            [1, "cQlM1"],
            [2, "cQlM2"],
            [3, "cQl31"],
            [4, "cQl32"],
            [5, "cQe1"],
            [6, "cQe2"],
            [7, "ctl1"],
            [8, "ctl2"],
            [9, "cte1"],
            [10, "cte2"],
            [13, "cQlM3"],
            [14, "cQl33"],
            [15, "cQe3"],
            [16, "ctl3"],
            [17, "cte3"],
            [19, "ctlS3"],
            [20, "ctlT3"],
            [21, "cblS3"]
        ],
        "DIM64F4L": [
            [1, "cll1111"],
            [2, "cll2222"],
            [3, "cll3333"],
            [4, "cll1122"],
            [5, "cll1133"],
            [6, "cll2233"],
            [7, "cll1221"],
            [8, "cll1331"],
            [9, "cll2332"]
        ]
    } 

    full_ops = [i[1] for key in smeftatnlo.keys()
           for i in smeftatnlo[key]]


    # revert dictionary 
    fd = {}
    for op in full_ops:
       for key in smeftatnlo.keys():
          for item in smeftatnlo[key]:
             if item[1] == op:
                fd[op] = [key, item[0]] 



    print("---> Start")
    
    # dop = args.default_operators.split(",")
    dop = args.op

    f = open(args.out, "w")
    
    f.write("change helicity False\n")
    f.write("change rwgt_dir rwgt\n")
    f.write("change mode NLO\n\n")
    #SM
    f.write("# SM rwgt_1\n")
    f.write("launch --rwgt_name=sm\n")
    for op in args.op:
        f.write("   set {} {} {}\n".format(fd[op][0], fd[op][1], 0))
    

    f.write("\n\n")
    
    
    # for Lin and Quad
    i = 2
    for op in args.op:
        for k in [-1,1]:
            f.write("# {}={} rwgt_{}\n".format(op, k, i))
            f.write("launch --rwgt_name={}\n".format(op.lower() if k==1 else (op+"_m1").lower()))
            for op2 in args.op:
                if op2 != op:
                    f.write("   set {} {} {}\n".format(fd[op2][0], fd[op2][1], 0))
                else:
                    f.write("   set {} {} {}\n".format(fd[op][0], fd[op][1], k))  
            i+=1    
            f.write("\n\n")
                             
    for ops in list(combinations(args.op,2)):
        f.write("# {}={}, {}={} rwgt_{}\n".format(ops[0], 1, ops[1], 1, i))
        f.write("launch --rwgt_name={}_{}\n".format(ops[0].lower(), ops[1].lower()))
        for op3 in args.op:
            if not op3 in ops:
                 f.write("   set {} {} {}\n".format(fd[op3][0], fd[op3][1], 0))
            else:
                 f.write("   set {} {} {}\n".format(fd[op3][0], fd[op3][1], 1)) 
                
        i+=1
                
        f.write("\n\n") 

    print("---> Done")

from itertools import combinations
import argparse
import os
import sys 

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-op","--op", help="Operator list to make the reweight card follwoing algebra" , nargs="+", required=True)
    parser.add_argument("-o", "--out", help="Out file name", required=True)
    parser.add_argument("-cr", "--change_model", help="Add a change model line to add new restriction at each reweight point", required=False, action="store_true")
    parser.add_argument("-dop", "--default_operators", nargs = "+", help="Comma separated list of operators that are turned on in the proc card. Will be set to zero in the reweight cards for SM", required=False, default="")
    parser.add_argument("-topU3l", "--topU3l", action="store_true", default=False, help="flag to select topU3l operators, by default U35 operators involved")
    args = parser.parse_args()



    params = [
        (1, "cQlM1", "DIM64F2L", 1),
        (2, "cQlM2", "DIM64F2L", 2),
        (3, "cQl31", "DIM64F2L", 3),
        (4, "cQl32", "DIM64F2L", 4),
        (5, "cQe1", "DIM64F2L", 5),
        (6, "cQe2", "DIM64F2L", 6),
        (7, "ctl1", "DIM64F2L", 7),
        (8, "ctl2", "DIM64F2L", 8),
        (9, "cte1", "DIM64F2L", 9),
        (10, "cte2", "DIM64F2L", 10),
        (11, "cQlM3", "DIM64F2L", 13),
        (12, "cQl33", "DIM64F2L", 14),
        (13, "cQe3", "DIM64F2L", 15),
        (14, "ctl3", "DIM64F2L", 16),
        (15, "cte3", "DIM64F2L", 17),
        (16, "ctlS3", "DIM64F2L", 19),
        (17, "ctlT3", "DIM64F2L", 20),
        (18, "cblS3", "DIM64F2L", 21),
    
        (19, "cQq83", "DIM64F", 1),
        (20, "cQq81", "DIM64F", 2),
        (21, "cQu8", "DIM64F", 3),
        (22, "ctq8", "DIM64F", 4),
        (23, "cQd8", "DIM64F", 6),
        (24, "ctu8", "DIM64F", 7),
        (25, "ctd8", "DIM64F", 8),
        (26, "cQq13", "DIM64F", 10),
        (27, "cQq11", "DIM64F", 11),
        (28, "cQu1", "DIM64F", 12),
        (29, "ctq1", "DIM64F", 13),
        (30, "cQd1", "DIM64F", 14),
        (31, "ctu1", "DIM64F", 16),
        (32, "ctd1", "DIM64F", 17),
        (33, "cQQ8", "DIM64F", 19),
        (34, "cQQ1", "DIM64F", 20),
        (35, "cQt1", "DIM64F", 21),
        (36, "ctt1", "DIM64F", 23),
        (37, "cQt8", "DIM64F", 25),
    
        (38, "cll1111", "DIM64F4L", 1),
        (39, "cll2222", "DIM64F4L", 2),
        (40, "cll3333", "DIM64F4L", 3),
        (41, "cll1122", "DIM64F4L", 4),
        (42, "cll1133", "DIM64F4L", 5),
        (43, "cll2233", "DIM64F4L", 6),
        (44, "cll1221", "DIM64F4L", 7),
        (45, "cll1331", "DIM64F4L", 8),
        (46, "cll2332", "DIM64F4L", 9),
    
        (47, "Lambda", "DIM6", 1),
        (48, "cpDC", "DIM6", 2),
        (49, "cpWB", "DIM6", 3),
        (50, "cdp", "DIM6", 4),
        (51, "cp", "DIM6", 5),
        (52, "cWWW", "DIM6", 6),
        (53, "cG", "DIM6", 7),
        (54, "cpG", "DIM6", 8),
        (55, "cpW", "DIM6", 9),
        (56, "cpBB", "DIM6", 10),
    
        (57, "cpl1", "DIM62F", 1),
        (58, "cpl2", "DIM62F", 2),
        (59, "cpl3", "DIM62F", 3),
        (60, "c3pl1", "DIM62F", 4),
        (61, "c3pl2", "DIM62F", 5),
        (62, "c3pl3", "DIM62F", 6),
        (63, "cpe", "DIM62F", 7),
        (64, "cpmu", "DIM62F", 8),
        (65, "cpta", "DIM62F", 9),
        (66, "cpqMi", "DIM62F", 10),
        (67, "cpq3i", "DIM62F", 11),
        (68, "cpQ3", "DIM62F", 12),
        (69, "cpQM", "DIM62F", 13),
        (70, "cpu", "DIM62F", 14),
        (71, "cpt", "DIM62F", 15),
        (72, "cpd", "DIM62F", 16),
        (73, "ctp", "DIM62F", 19),
        (74, "ctZ", "DIM62F", 22),
        (75, "ctW", "DIM62F", 23),
        (76, "ctG", "DIM62F", 24)
    ]

    param_dict = {item[1]: {'block': item[2], 'value': item[3]} for item in params}

    full_ops = param_dict
    if args.topU3l: full_ops = param_dict
    
    # begin
    print("---> Start")
    
    # dop = args.default_operators.split(",")
    dop = args.default_operators

    f = open(args.out, "w")
    
    f.write("change helicity False\n")
    f.write("change rwgt_dir rwgt\n\n")
    f.write("change mode NLO\n\n")
    #SM
    f.write("# SM rwgt_1\n")
    f.write("launch --rwgt_name=sm\n")
    if not args.default_operators:
       for op in args.op:
           f.write("   set {} {} {}\n".format(full_ops[op]['block'], full_ops[op]['value'], 0))
    
    else:
       for op in dop:
          f.write("   set {} {} {}\n".format(full_ops[op]['block'], full_ops[op]['value'], 0))

    f.write("\n\n")
    
    
    # for Lin and Quad
    i = 2
    for op in args.op:
        for k in [-1.0,1.0]:
            # if op in ["cQlM1", "cQlM2", "cQlM3", "cQl31", "cQl32", "cQl33", "cQe1", "cQe2", "cQe3"] : k = k*50
            f.write("# {}={} rwgt_{}\n".format(op, k, i))
            if args.change_model:
               f.write("change rwgt_dir rwgt_{}\n".format(op.lower() if k>0 else op.lower()+"_m1"))
               f.write("change model SMEFTsim_U35_MwScheme_UFO-{}_massless\n".format(op.lower() if k>0 else op.lower()+"_m1"))
               f.write("launch --rwgt_name={}\n".format(op.lower() if k>0 else op.lower()+"_m1"))
               #f.write("models/SMEFTsim_U35_MwScheme_UFO/restrict_{}_massless.dat\n".format(op if k==1 else op+"_m1"))
            else:
               f.write("launch --rwgt_name={}\n".format(op.lower() if k>0 else op.lower()+"_m1"))
               for op2 in args.op:
                   
                   if op2 != op:
                       f.write("   set {} {} {}\n".format(full_ops[op2]['block'], full_ops[op2]['value'], 0))
                   else:
                       f.write("   set {} {} {}\n".format(full_ops[op]['block'], full_ops[op]['value'], k))  
            i+=1    
            f.write("\n\n")
                             
    for ops in list(combinations(args.op,2)):
        f.write("# {}={}, {}={} rwgt_{}\n".format(ops[0], 1.0 if ops[0] not in ["cQlM1", "cQlM2", "cQlM3", "cQl31", "cQl32", "cQl33", "cQe1", "cQe2", "cQe3"] else 1.0, ops[1], 1.0 if ops[1] not in ["cQlM1", "cQlM2", "cQlM3", "cQl31", "cQl32", "cQl33", "cQe1", "cQe2", "cQe3"] else 1.0, i))
        if args.change_model:
           f.write("change rwgt_dir rwgt_{}_{}\n".format(ops[0], ops[1])) 
           if os.path.isfile("SMEFTsim_U35_MwScheme_UFO/restrict_{}_{}_massless.dat".format(ops[0], ops[1])):
              f.write("change model SMEFTsim_U35_MwScheme_UFO-{}_{}_massless\n".format(ops[0], ops[1]))
              f.write("launch --rwgt_name={}_{}\n".format(ops[0].lower(), ops[1].lower()))
              #f.write("models/SMEFTsim_U35_MwScheme_UFO/restrict_{}_{}_massless.dat\n".format(ops[0], ops[1]))
           elif os.path.isfile("SMEFTsim_U35_MwScheme_UFO/restrict_{}_{}_massless.dat".format(ops[1], ops[0])):
              f.write("change model SMEFTsim_U35_MwScheme_UFO-{}_{}_massless\n".format(ops[1], ops[0]))
              f.write("launch --rwgt_name={}_{}\n".format(ops[0].lower(), ops[1].lower()))
              #f.write("models/SMEFTsim_U35_MwScheme_UFO/restrict_{}_{}_massless.dat\n".format(ops[1], ops[0]))
           else: sys.exit("[ERROR] No restriction card in SMEFTsim_U35_MwScheme_UFO for op pair {}".format(ops))

        else:

           f.write("launch --rwgt_name={}_{}\n".format(ops[0].lower(), ops[1].lower()))
           for op3 in args.op:
               if not op3 in ops:
                    f.write("   set {} {} {}\n".format(full_ops[op3]['block'], full_ops[op3]['value'], 0))
               else:
                    f.write("   set {} {} {}\n".format(full_ops[op3]['block'], full_ops[op3]['value'], 1.0 if op3 not in ["cQlM1", "cQlM2", "cQlM3", "cQl31", "cQl32", "cQl33", "cQe1", "cQe2", "cQe3"] else 1.0)) 
                
        i+=1
                
        f.write("\n\n") 

    print("---> Done")

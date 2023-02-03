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


    operators_topU3l = {'cbGRe': '21', 'cju1': '66', 'ctj1': '70', 'cju8': '68', 'ctd1': '58', 'ctj8': '71', 'cHBtil': '5', 'cQQ8': '45', 'cbHRe': '13', 'cutbd8Im': '26', 'cQQ1': '44', 'cll': '106', 'ctb8': '61', 'cld': '121', 'cle': '123', 'ctb1': '57', 'cQtjd8Re': '91', 'ctWIm': '10', 'clu': '119', 'cQtQb1Re': '98', 'cee': '112', 'ced': '115', 'cjQtu8Re': '83', 'cQd1': '76', 'ceu': '113', 'cQd8': '77', 'cjtQd8Re': '97', 'cHQ3': '29', 'cHQ1': '27', 'cQt1': '72', 'cleQt1Im': '52', 'cjd1': '74', 'cleju3Re': '128', 'cQujb8Re': '95', 'cQl1': '110', 'cjd8': '75', 'cdHRe': '12', 'cutbd1Im': '25', 'cHWBtil': '6', 'ctGIm': '8', 'ctGRe': '15', 'cjujd8Im': '32', 'cHGtil': '3', 'cledjIm': '48', 'cjtQd1Im': '41', 'cuu1': '46', 'ceWIm': '46', 'cHWtil': '4', 'cHWB': '9', 'cHl3': '104', 'cuu8': '47', 'cuGRe': '14', 'cdWIm': '15', 'cud1': '56', 'cdWRe': '22', 'cQt8': '73', 'cuGIm': '7', 'cud8': '60', 'cbWRe': '23', 'cjuQb8Re': '93', 'cHbox': '4', 'cbHIm': '22', 'ceBRe': '102', 'cjujd81Im': '34', 'cQujb1Re': '94', 'cuBRe': '18', 'cbBRe': '25', 'cdGIm': '13', 'ctWRe': '17', 'cHudIm': '23', 'ctt': '48', 'cjtQd8Im': '42', 'cQu1': '67', 'cQl3': '111', 'cQu8': '69', 'cuWRe': '16', 'cuHRe': '10', 'cjujd1Re': '86', 'cdd8': '52', 'ctl': '120', 'clj3': '109', 'cQtQb1Im': '43', 'cdd1': '51', 'cjQbd8Re': '85', 'cuHIm': '19', 'cbu8': '63', 'cuBIm': '11', 'ctBIm': '12', 'ceHIm': '45', 'cGtil': '1', 'ctu1': '49', 'ceBIm': '47', 'cHl1': '103', 'cbGIm': '14', 'ctu8': '50', 'cll1': '107', 'cjuQb1Re': '92', 'cHtbIm': '24', 'cQtQb8Re': '99', 'cQj38': '43', 'cH': '3', 'cjQbd8Im': '30', 'cQj31': '42', 'cG': '1', 'cHDD': '5', 'cjujd8Re': '87', 'cW': '2', 'cjQbd1Re': '84', 'cleju3Im': '51', 'ctHIm': '20', 'cjujd81Re': '89', 'cjujd11Re': '88', 'cQujb1Im': '39', 'cHB': '8', 'cjujd11Im': '33', 'cbj1': '78', 'cdBRe': '24', 'cledjRe': '124', 'cdBIm': '17', 'cbj8': '79', 'cdHIm': '21', 'cleQt3Im': '53', 'ctBRe': '19', 'cQtjd8Im': '36', 'cQtQb8Im': '44', 'cQtjd1Im': '35', 'cjj38': '39', 'clebQRe': '125', 'cdGRe': '20', 'cleju1Re': '126', 'clebQIm': '49', 'cjj31': '38', 'cbb': '53', 'cleju1Im': '50', 'cbe': '116', 'cbu1': '59', 'ctHRe': '11', 'cbl': '122', 'cQj11': '40', 'cHtbRe': '35', 'cQj18': '41', 'cjuQb1Im': '37', 'clj1': '108', 'cWtil': '2', 'ceHRe': '100', 'ctd8': '62', 'cte': '114', 'cutbd1Re': '64', 'cHj3': '28', 'cHj1': '26', 'cje': '117', 'cbWIm': '16', 'cjQtu1Im': '27', 'cjQbd1Im': '29', 'cjj18': '37', 'ceWRe': '101', 'cHudRe': '34', 'cHd': '32', 'cHe': '105', 'cjQtu1Re': '82', 'cbBIm': '18', 'cjtQd1Re': '96', 'cjQtu8Im': '28', 'cQe': '118', 'cHt': '31', 'cHu': '30', 'cleQt1Re': '127', 'cjuQb8Im': '38', 'cjujd1Im': '31', 'cQb8': '81', 'cleQt3Re': '129', 'cHG': '6', 'cuWIm': '9', 'cjj11': '36', 'cQb1': '80', 'cQujb8Im': '40', 'cbd8': '55', 'cutbd8Re': '65', 'cHbq': '33', 'cHW': '7', 'cQtjd1Re': '90', 'cbd1': '54'}
    


    operators_u35 = {
        'cG': 1,
        'cW': 2,
        'cH': 3,
        'cHbox': 4,
        'cHDD': 5,
        'cHG': 6,
        'cHW': 7,
        'cHB': 8,
        'cHWB': 9,
        'ceHRe': 10,
        'cuHRe': 11,
        'cdHRe': 12,
        'ceWRe': 13,
        'ceBRe': 14,
        'cuGRe': 15,
        'cuWRe': 16,
        'cuBRe': 17,
        'cdGRe': 18,
        'cdWRe': 19,
        'cdBRe': 20,
        'cHl1': 21,
        'cHl3': 22,
        'cHe': 23,
        'cHq1': 24,
        'cHq3': 25,
        'cHu': 26,
        'cHd': 27,
        'cHudRe': 28,
        'cll': 29,
        'cll1': 30,
        'cqq1': 31,
        'cqq11': 32,
        'cqq3': 33,
        'cqq31': 34,
        'clq1': 35,
        'clq3': 36,
        'cee': 37,
        'cuu': 38,
        'cuu1': 39,
        'cdd': 40,
        'cdd1': 41,
        'ceu': 42,
        'ced': 43,
        'cud1': 44,
        'cud8': 45,
        'cle': 46,
        'clu': 47,
        'cld': 48,
        'cqe': 49,
        'cqu1': 50,
        'cqu8': 51,
        'cqd1': 52,
        'cqd8': 53,
        'cledqRe': 54,
        'cquqd1Re': 55,
        'cquqd11Re': 56,
        'cquqd8Re': 57,
        'cquqd81Re': 58,
        'clequ1Re': 59,
        'clequ3Re': 60
    }

    full_ops = operators_u35
    if args.topU3l: full_ops = operators_topU3l
    
    # begin
    print("---> Start")
    
    # dop = args.default_operators.split(",")
    dop = args.default_operators

    f = open(args.out, "w")
    
    f.write("change helicity False\n")
    f.write("change rwgt_dir rwgt\n\n")
    #SM
    f.write("# SM rwgt_1\n")
    f.write("launch --rwgt_name=SM\n")
    if not args.default_operators:
       for op in args.op:
           f.write("   set SMEFT {} {}\n".format(full_ops[op], 0))
    
    else:
       for op in dop:
          f.write("   set SMEFT {} {}\n".format(full_ops[op], 0))

    f.write("\n\n")
    
    
    # for Lin and Quad
    i = 2
    for op in args.op:
        for k in [-1,1]:
            f.write("# {}={} rwgt_{}\n".format(op, k, i))
            if args.change_model:
               f.write("change rwgt_dir rwgt_{}\n".format(op if k==1 else op+"_m1"))
               f.write("change model SMEFTsim_U35_MwScheme_UFO-{}_massless\n".format(op if k==1 else op+"_m1"))
               f.write("launch --rwgt_name={}\n".format(op if k==1 else op+"_m1"))
               #f.write("models/SMEFTsim_U35_MwScheme_UFO/restrict_{}_massless.dat\n".format(op if k==1 else op+"_m1"))
            else:
               f.write("launch --rwgt_name={}\n".format(op if k==1 else op+"_m1"))
               for op2 in args.op:
                   
                   if op2 != op:
                       f.write("   set SMEFT {} {}\n".format(full_ops[op2], 0))
                   else:
                       f.write("   set SMEFT {} {}\n".format(full_ops[op], k))  
            i+=1    
            f.write("\n\n")
                             
    for ops in list(combinations(args.op,2)):
        f.write("# {}={}, {}={} rwgt_{}\n".format(ops[0], 1, ops[1], 1, i))
        if args.change_model:
           f.write("change rwgt_dir rwgt_{}_{}\n".format(ops[0], ops[1])) 
           if os.path.isfile("SMEFTsim_U35_MwScheme_UFO/restrict_{}_{}_massless.dat".format(ops[0], ops[1])):
              f.write("change model SMEFTsim_U35_MwScheme_UFO-{}_{}_massless\n".format(ops[0], ops[1]))
              f.write("launch --rwgt_name={}_{}\n".format(ops[0], ops[1]))
              #f.write("models/SMEFTsim_U35_MwScheme_UFO/restrict_{}_{}_massless.dat\n".format(ops[0], ops[1]))
           elif os.path.isfile("SMEFTsim_U35_MwScheme_UFO/restrict_{}_{}_massless.dat".format(ops[1], ops[0])):
              f.write("change model SMEFTsim_U35_MwScheme_UFO-{}_{}_massless\n".format(ops[1], ops[0]))
              f.write("launch --rwgt_name={}_{}\n".format(ops[0], ops[1]))
              #f.write("models/SMEFTsim_U35_MwScheme_UFO/restrict_{}_{}_massless.dat\n".format(ops[1], ops[0]))
           else: sys.exit("[ERROR] No restriction card in SMEFTsim_U35_MwScheme_UFO for op pair {}".format(ops))

        else:

           f.write("launch --rwgt_name={}_{}\n".format(ops[0], ops[1]))
           for op3 in args.op:
               if not op3 in ops:
                    f.write("   set SMEFT {} {}\n".format(full_ops[op3], 0))
               else:
                    f.write("   set SMEFT {} {}\n".format(full_ops[op3], 1)) 
                
        i+=1
                
        f.write("\n\n") 

    print("---> Done")

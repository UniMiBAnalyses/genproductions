import os, stat
import sys
import argparse
import copy
import subprocess
import time
from glob import glob
from operator import itemgetter

def get_folder_size(path):
    size = 0.
    for path, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(path, f)
            if os.path.isfile(fp): size += os.path.getsize(fp)

    return size

def build_reweight_card(rD, change_process, output):

    mandatory = ["change helicity False\n"]
    mandatory.append("change rwgt_dir rwgt\n")

    change_process = change_process.split(",")

    if len(change_process) > 0: 
        for i in range(len(change_process)):
            change_process[i] += "\n"
        mandatory += change_process

    mandatory.append("\n")

    f = open(output[0], "w")

    for j in mandatory: 
        f.write(j)


    f.write("\n")

    for key in rD.keys():
        
        for line in rD[key]:
            if line not in mandatory:
                f.write(line)
        
        f.write("\n")
    
    f.close() 

    for path in output[1:]: 
        os.system("cp {} {}".format(output[0], path))

    return


def make_tarball(WORKDIR, iscmsconnect, PRODHOME, CARDSDIR, CARDNAME, scram_arch, cmssw_version):

    # NEEDS CMSENV
    # so we immerge the script in an external executable thagt will run in a child process
    print("---> Creating tarball")
    os.chdir("{WORKDIR}".format(WORKDIR=WORKDIR))

    f = open("compress.sh", "w")

    f.write("echo  \"---> Creating tarball\"\n")
    f.write("eval `scram runtime -sh`\n")

    f.write("cd gridpack\n")

    f.write("if [ {} -gt 0 ]; then\n".format(1 if iscmsconnect else 0))
    f.write("    XZ_OPT=\"--lzma2=preset=2,dict=256MiB\"\n")
    f.write("else\n")
    f.write("    XZ_OPT=\"--lzma2=preset=9,dict=512MiB\"\n")
    f.write("fi\n")
    f.write("\n")
    f.write("if [ -d InputCards ]; then\n") 
    f.write("  rm -rf InputCards\n")
    f.write("fi\n")

    f.write("mkdir -p InputCards\n")
    f.write("cp {CARDSDIR}/{CARDNAME}*.* InputCards\n".format(CARDSDIR=CARDSDIR, CARDNAME=CARDNAME))

    f.write("echo  \"-->tarring\"\n")
    
    f.write("EXTRA_TAR_ARGS=\"\"\n")
    f.write("if [ -e {CARDSDIR}/{CARDNAME}_externaltarball.dat ]; then\n".format(CARDSDIR=CARDSDIR, CARDNAME=CARDNAME))
    f.write("    EXTRA_TAR_ARGS=\"external_tarball header_for_madspin.txt \"\n")
    f.write("fi\n")
    f.write("### include merge.pl script for LO event merging\n")
    f.write("if [ -e merge.pl ]; then\n")
    f.write("    EXTRA_TAR_ARGS+=\"merge.pl \"\n")
    f.write("fi\n")
    f.write("XZ_OPT=\"$XZ_OPT\" tar -cJpsvf {PRODHOME}/{CARDNAME}_{scram_arch}_{cmssw_version}_tarball.tar.xz mgbasedir process *.sh InputCards ${{EXTRA_TAR_ARGS}}\n".format( PRODHOME=PRODHOME, CARDNAME=CARDNAME, scram_arch=scram_arch, cmssw_version=cmssw_version ))

    f.write("echo \"Gridpack created successfully at {PRODHOME}/{CARDNAME}_{scram_arch}_{cmssw_version}_tarball.tar.xz\"".format(PRODHOME=PRODHOME, CARDNAME=CARDNAME, scram_arch=scram_arch, cmssw_version=cmssw_version))
    f.write("echo \"End of job\"\n")
    f.write("cd ..\n")

    f.close()


    #make file executable
    st = os.stat("compress.sh")
    os.chmod("compress.sh", st.st_mode | stat.S_IEXEC)

    print("RUN")
    # run it
    os.system("./compress.sh")

    # remove it so it won't be tarred in the gridpack
    os.system("rm compress.sh")

    return


def mkdir(path):
    try:
        os.system("mkdir -p {}".format(path))
    except:
        print("Directory {} already present, skipping".format(path))
        pass
    
    return 


def write_sh(exec_name, card_name, card_dir, sub_folder, output_folder):
    l = """#! /bin/bash
# Condor scratch dir
condor_scratch=$(pwd)


# Add unzip to the environment
if [ -x $condor_scratch/unzip ]; then
    mkdir $condor_scratch/local_bin
    mv $condor_scratch/unzip $condor_scratch/local_bin
    export PATH="$PATH:$condor_scratch/local_bin"
fi
# Untar input files
ls
tar xfz "{input_files}"

cp {sub_folder}/{exec_name}.dat ${{condor_scratch}}/{card_name}/{card_name}_gridpack/work/process/madevent/Cards/reweight_card.dat
cp {sub_folder}/{exec_name}.dat ${{condor_scratch}}/{card_dir}/{card_name}_reweight_card.dat

echo "mg5_path = ${{condor_scratch}}/{card_name}/{card_name}_gridpack/work/MG5_aMC_v2_6_5" >> ${{condor_scratch}}/{card_name}/{card_name}_gridpack/work/process/madevent/Cards/me5_configuration.txt

echo "cluster_temp_path = None" >> ${{condor_scratch}}/{card_name}/{card_name}_gridpack/work/process/madevent/Cards/me5_configuration.txt
echo "run_mode = 0" >> ${{condor_scratch}}/{card_name}/{card_name}_gridpack/work/process/madevent/Cards/me5_configuration.txt 

# Setup CMS framework
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

# For modified gridpack generation script set this variable to exit after reweight and not create the tarball
export REWEIGHT_ON_CONDOR=true


# Purdue wokaround
unset CXX CC FC
# Run
iscmsconnect=1 bash -x gridpack_generation_EFT.sh {card_name} {card_dir} local REWEIGHT
exitcode=$?
if [ $exitcode -ne 0 ]; then
    echo "Something went wrong while running REWEIGHT step. Exiting now."
    exit $exitcode
fi
# Pack output and condor scratch dir info
cd "${{condor_scratch}}/{card_name}/{card_name}_gridpack/work/process/madevent"

# Remove All EPS files, they weight A LOT
rm rwgt/*/*/SubProcesses/P*/*.ps

# rwgt directory name
cd rwgt
XZ_OPT="--lzma2=preset=9,dict=512MiB" tar -cJpsf "${{condor_scratch}}/{sandbox_output}" "{rwgt_name}"


# Stage-out sandbox
# First, try XRootD via stash.osgconnect.net
echo ">> Copying sandbox via XRootD"
xrdcp -f "${{condor_scratch}}/{sandbox_output}" "root://stash.osgconnect.net:1094/${{stash_tmpdir##/stash}}/{sandbox_output}"
exitcode=$?
if [ $exitcode -eq 0 ]; then
    exit 0
else
    echo "The xrdcp command below failed:"
    echo "xrdcp -f ${{condor_scratch}}$sandbox_output root://stash.osgconnect.net:1094/${{stash_tmpdir##/stash}}/$sandbox_output"
fi
""".format(sub_folder=sub_folder, sandbox_output="{}_output.tar.xz".format(exec_name) , input_files="input_reweight_{}.tar.gz".format(card_name), card_name=card_name, card_dir=card_dir, exec_name=exec_name, rwgt_name=exec_name.split("_" + card_name)[0])

    f = open(output_folder + exec_name + ".sh", "w")
    f.write(l)
    f.close()

    os.system("chmod +x {}".format(output_folder + exec_name + ".sh"))
    return  

def write_jdl(exec_name, card_name, card_dir, output_folder):
    l = """Universe = vanilla 
Executable = {exec_name}.sh
Arguments = {card_name} {card_dir}

Error = condor_log/job.err.$(Cluster)-$(Process) 
Output = condor_log/job.out.$(Cluster)-$(Process) 
Log = condor_log/job.log.$(Cluster) 

transfer_input_files = input_reweight_{card_name}.tar.gz, gridpack_generation_EFT.sh, /usr/bin/unzip
transfer_output_files = {card_name}.log, {exec_name}_output.tar.xz
transfer_output_remaps = \"{card_name}.log = {exec_name}.log\"
+WantIOProxy=true
+IsGridpack=true
+GridpackCard = \"{card_name}\"

+REQUIRED_OS = \"rhel7\"
request_cpus = 2
request_memory = 5Gb
Queue 1
""".format(exec_name=exec_name, card_name=card_name, card_dir=card_dir )

    f = open(output_folder + exec_name + ".jdl", "w")
    f.write(l)
    f.close()
    return 

def write_rew_dict(rew_dict, output_folder, cardname, cardpath, sub_folder):

    if not output_folder[-1] == "/": output_folder += "/"

    for key in rew_dict.keys():
        
        # writing reweight card
        f = open(output_folder + "rwgt_{}_{}.dat".format(key, cardname), "w")
        for line in rew_dict[key]:
            f.write(line)
        f.close() 

        #writing .jdl
        write_jdl("rwgt_{}_{}".format(key, cardname), cardname, cardpath, output_folder="")

        #writing .sh
        write_sh("rwgt_{}_{}".format(key, cardname), cardname, cardpath, sub_folder, output_folder="")

    return 

def build_rew_dict_scratch(operators, change_process , model, append_SM=False):

    rew_d = {}

    mandatory = ["change helicity False\n"]
    mandatory.append("change rwgt_dir rwgt\n")

    change_process = change_process.split(",")

    if len(change_process) > 0: 
        for i in range(len(change_process)):
            change_process[i] += "\n"
        mandatory += change_process

    mandatory.append("\n")
    
    sortedsel = sorted (operators, key = itemgetter (1))

    # We take all 2D combinations of operators, we then reweight to the following
    # components (1,0), (-1,0), (0,1), (0,-1), (1,1) as the matrix element
    # is the same. This is more efficient than generating 5 different reweight dirs.
    # Howvere we need to keep track of the single operators (the (1,0) (0,1)) already studied
    # For the other we just evaluate (1,1)

    done_singles = []

    counter_mix = 0
    counter_single = 0

    if append_SM:
        tag="SM"
        rwgt_points = []
        rwgt_points += mandatory

        # first append a comment line
        rwgt_points.append("# SM\n")
        # change rwgt direcrory 
        rwgt_points.append("change rwgt_dir rwgt/rwgt_{}\n".format(tag))
        # change model
        rwgt_points.append("change model {}-SMlimit_massless\n".format(model))
        # evaluate the mixed term (1,1)
        rwgt_points.append("\n")
        rwgt_points.append("launch --rwgt_name=SM\n")
        # idx += 1

        rwgt_points.append("\n")
        rwgt_points.append("\n")

        rew_d[tag] = copy.copy(rwgt_points)

    idx = 1
    for i in range (len (sortedsel)):
        for j in range (i+1, len (sortedsel)):
            tag = sortedsel[i][1] + '_' + sortedsel[j][1] 
            ov_tag = sortedsel[i][1] + '_' + sortedsel[j][1] 
            
            rwgt_points = []
            rwgt_points += mandatory

            # first append a comment line
            rwgt_points.append("# {}=1 {}=1 rwgt_{} {}\n".format(sortedsel[i][1] , sortedsel[j][1], sortedsel[i][1] + "_" + sortedsel[j][1], idx))
            # change rwgt direcrory 
            rwgt_points.append("change rwgt_dir rwgt/rwgt_{}\n".format(tag))
            # change model
            rwgt_points.append("change model {}-{}_massless\n".format(model, tag))
            # evaluate the mixed term (1,1)
            rwgt_points.append("\n")
            rwgt_points.append("launch --rwgt_name={}\n".format(sortedsel[i][1] + "_" + sortedsel[j][1]))
            idx += 1

            rwgt_points.append("\n")
            rwgt_points.append("\n")

            rew_d[ov_tag] = copy.copy(rwgt_points)

            # check if first operator already gen
            if not sortedsel[i][0] in done_singles:
                # If not then evaluate (1,0) and (-1,0)
                for val in [-1 ,1]:
                    tag = sortedsel[i][1]
                    if val == -1: tag += "m1"
                    rwgt_single_point = []
                    rwgt_single_point += mandatory
                    rwgt_single_point.append("# {}={} {}\n".format(sortedsel[i][1], val, idx))

                    rwgt_single_point.append("change rwgt_dir rwgt/rwgt_{}\n".format(tag))
                    rwgt_single_point.append("change model {}-{}_massless\n".format(model, tag))

                    rwgt_single_point.append("launch --rwgt_name={}\n".format(tag))
                    
                    rwgt_single_point.append("\n")
                    idx += 1
                    counter_single += 1

                    rew_d[tag] = copy.copy(rwgt_single_point)

                done_singles.append(sortedsel[i][0])

            # check if second operator already gen
            if not sortedsel[j][0] in done_singles:
                # If not then evaluate (1,0) and (-1,0)
                for val in [-1 ,1]:
                    tag = sortedsel[j][1]
                    if val == -1: tag += "m1"
                    rwgt_single_point = []
                    rwgt_single_point += mandatory
                    rwgt_single_point.append("# {}={} {}\n".format(sortedsel[j][1], val, idx))

                    rwgt_single_point.append("change rwgt_dir rwgt/rwgt_{}\n".format(tag))
                    rwgt_single_point.append("change model {}-{}_massless\n".format(model, tag))

                    rwgt_single_point.append("launch --rwgt_name={}\n".format(tag))
                    
                    rwgt_single_point.append("\n")
                    idx += 1
                    counter_single += 1

                    rew_d[tag] = copy.copy(rwgt_single_point)

                done_singles.append(sortedsel[j][0])

        
            counter_mix += 1
    
    print("--> Total mixed op = " + str(counter_mix))
    print("--> Total single op (+1 and -1 summed). Should be equal to Nops * 2 = " + str(counter_single))
    return rew_d


def build_rew_dict(rew_card):
    f = open(rew_card, 'r')
    contents = f.readlines()

    rew_d = {}

    try:
        contents.index("change rwgt_dir rwgt\n")
    except: 
        sys.exit("[ERROR] \"change rwgt_dir rwgt\" must be present in reweight card")

    #find first launch index 
    for idx,l in enumerate(contents):
        if "launch" in l: break 

    reweight_template = contents[:idx+1]

    tag = ""
    for i in contents:
        if "change rwgt_dir rwgt/" in i: 
            tag = i.split("change rwgt_dir rwgt/")[1].split("\n")[0]

    #rew_d[idx] = reweight_template
    rew_d[tag] = reweight_template

    contents = contents[idx+1:]
    idx = 1

    reweight_template_copy = copy.copy(reweight_template)
    tag = ""
    for line in contents:
        if "launch" not in line:
            if "change model" in line:
                for id_, line_ in enumerate(reweight_template_copy):
                    if "change model" in line_:
                        reweight_template_copy[id_] = line 

            if "change process" in line:
                for id_, line_ in enumerate(reweight_template_copy):
                    if "change process" in line_:
                        reweight_template_copy[id_] = line 

            if "change rwgt_dir" in line:
                for id_, line_ in enumerate(reweight_template_copy):
                    if "change rwgt_dir" in line_ and line_ != "change rwgt_dir rwgt\n":
                        tag = line.split("/")[-1].split("\n")[0]
                        nf = "change rwgt_dir rwgt/" + line.split("/")[-1]
                        reweight_template_copy[id_] = nf 

        else: 
            reweight_template_copy[-1] = line 
            #rew_d[idx] =  copy.copy(reweight_template_copy)
            rew_d[tag] =  copy.copy(reweight_template_copy)
            idx += 1
            reweight_template_copy = copy.copy(reweight_template)
            tag = ""

    return rew_d


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Command line parser')
    parser.add_argument('-cn', '--cardname',                    dest='cardname',            help='The name of the cards, <name>_proc_card.dat', required = True)
    parser.add_argument('-cp', '--cardpath',                    dest='cardpath',            help='The path to the cards directory', required = True)
    parser.add_argument('-t', '--task',                         dest='task',                help='Tasks to be executed (separated by a space). Default is all. Can choose between: rew (only write rew cards and execs),\n tar (Create tarball of input gridpack),\n sub (submit all jobs),\n mv (move all results once jobs are finished in the right position),\n clean (clean all files created that are not useful),\n prepare (prepare final gridpack, set of sed and paths),\n compress (create the final gridpack)\n createsymlink (rw_me directories are a waste of space. Just retain one and create sym links to the first)', required = False, nargs = "+", default=["all"])
    parser.add_argument('-sf', '--subfolder',                   dest='subfolder',           help='The path to the folder where .jid, exec and reweight cards will be saved', required = False, default="condor_sub")
    parser.add_argument('-is5f', '--is5FlavorScheme',           dest='is5FlavorScheme',     help='Is the gridpack intended for 5fs? Default is true', required = False, default=True, action="store_false")
    parser.add_argument('-scram', '--scramarch',                dest='scramarch',           help='Scram arch version required. Default is slc7_amd64_gcc700', required = False, default="slc7_amd64_gcc700", type=str)
    parser.add_argument('-cmssw', '--cmssw',                    dest='cmssw',               help='CMSSW version required. Default is CMSSW_10_6_19', required = False, default="CMSSW_10_6_19", type=str)
    parser.add_argument('-iscmsc', '--iscmsconnect',            dest='iscmsconnect',        help='Are you working on cmsconnect? Default is true', required = False, default=True, action="store_false")
    parser.add_argument('-cr', '--createreweight',              dest='createreweight',      help='File operator.py will be imported and restriction cards created', required = False, default=False, action="store_true")
    parser.add_argument('-add_sm_point', '--add_sm_point',      dest='add_sm_point',        help='When building the reweighting, this will also add the SM point (e.g. if your codegen and integrate started from an EFT point). Default is false!', required = False, default=False, action="store_true")
    parser.add_argument('-change_process', '--change_process',  dest='change_process',      help='If args.cr is specified, add this to change process in reweight card', required = False, default="", type=str)
    parser.add_argument('-m', '--model',                        dest='model',               help='If args.cr is specified, add this to change the baseline model. Default is SMEFTsim_topU3l_MwScheme_UFO_b_massless', required = False, default="SMEFTsim_topU3l_MwScheme_UFO_b_massless", type=str)
    parser.add_argument('-appendsm', '--appendsm',            dest='appendsm',        help='If turned on at reweight point also SMlimit massless model will be imported and weight computed', required = False, default=False, action="store_true")

    args = parser.parse_args()

    # Sanity checks

    if not os.path.isdir(args.cardpath): sys.exit("[ERROR] Path {} does not exist".format(args.cardpath))
    if not os.path.isdir(args.cardname): sys.exit("[ERROR] Path {} does not exist".format(args.cardname))
    if not os.path.isfile(args.cardpath + "/" + args.cardname + "_proc_card.dat"): sys.exit("[ERROR] proc card does not exist in {}".format(args.cardpath))
    if not os.path.isfile(args.cardpath + "/" + args.cardname + "_run_card.dat"): sys.exit("[ERROR]  run card does not exist in {}".format(args.cardpath))
    if not args.createreweight:
        if not os.path.isfile(args.cardpath + "/" + args.cardname + "_reweight_card.dat"): sys.exit("[ERROR]  reweight card does not exist in {}".format(args.cardpath))
    

    PRODHOME = os.getcwd()
    CARDSDIR=os.path.join(PRODHOME, args.cardpath)
    helpers_dir=os.path.join(PRODHOME, "Utilities")
    WORKDIR = os.path.join(PRODHOME, args.cardname, args.cardname+"_gridpack", "work") 
    genp_name = PRODHOME.split("/bin/MadGraph5_aMCatNLO")[0].split("/")[-1]
    script_dir=os.path.join(PRODHOME.split(genp_name)[0], "genproductions/", "Utilities/scripts")
    cmssw_version=args.cmssw
    scram_arch=args.scramarch
    MGBASEDIRORIG = "MG5_aMC_v2_6_5"
    patches_directory="./patches"
    utilities_dir="./Utilities"
    plugin_directory="./PLUGIN"


    ########### LOGGING GRIDPACK INFOS ############
    print("----> BEGIN <------")
    print("Production home: " + PRODHOME)
    print("Card Dir: " + CARDSDIR)
    print("Helpers Dir: " + helpers_dir)
    print("Working Dir: " + WORKDIR)
    print("CMSSW version: " + cmssw_version)
    print("SCRAM ARCH version: " + scram_arch)
    print("MADGRAPH Dir: " + MGBASEDIRORIG)
    


    input_files="input_reweight_{}.tar.gz".format(args.cardname)

    
    #create subfolder to store exec, jid and rew card
    mkdir(args.subfolder)
    # Parsing reweight card
    if not args.createreweight:
        rd = build_rew_dict(args.cardpath + "/" + args.cardname + "_reweight_card.dat")
    else:
        operators = []
        execfile("operators.py")
        rd = build_rew_dict_scratch(operators, args.change_process, args.model, append_SM=args.appendsm)
    
    if any(i in ["rew", "all"] for i in args.task ):
        # write the separate reweight point in a file
        write_rew_dict(rd, args.subfolder, args.cardname, args.cardpath, args.subfolder)
    
    if any(i in ["tar", "all"] for i in args.task ):
        if os.path.isfile(input_files) or os.path.isdir(input_files): 
            print("Tarball allready present. reusing")
        else:
            # move process directory if under gridpack:
            if os.path.isdir(args.cardname + "/" + args.cardname + "_gridpack/work/gridpack") and os.path.isdir(args.cardname + "/" + args.cardname + "_gridpack/work/gridpack/process"):
                print("--> Moving process directory from gridpack/process under work directory ")
                os.system("mv " + args.cardname + "/" + args.cardname + "_gridpack/work/gridpack/process " + WORKDIR)

            exclude_rwgt = ""
            if os.path.isdir(args.cardname + "/" + args.cardname + "_gridpack/work/gridpack"):
                exclude_rwgt += "--exclude " + args.cardname + "/" + args.cardname + "_gridpack/work/gridpack "
            if os.path.isdir(args.cardname + "/" + args.cardname + "_gridpack/work/process/madevent/rwgt"):
                exclude_rwgt += "--exclude " + args.cardname + "/" + args.cardname + "_gridpack/work/process/madevent/rwgt "
            
            if not os.path.isdir(args.cardname + "/" + args.cardname + "_gridpack/work/process"):
                if not os.path.isdir(args.cardname + "/" + args.cardname + "_gridpack/work/gridpack/process"):
                    sys.exit("[ERROR] No more process directory in the gridpack!")
                
                else:
                    os.system("cp -r " + args.cardname + "/" + args.cardname + "_gridpack/work/gridpack/process/!(madevent/rwgt) " + args.cardname + "/" + args.cardname + "_gridpack/work")

            

            print("tar {exclude} -zchvf \"{input_files}\" {rwgt_cards} \"{card_name}\" \"{card_dir}\" \"{patches_directory}\" \"{utilities_dir}\" \"{plugin_directory}\"".format(exclude=exclude_rwgt, input_files=input_files, rwgt_cards=" ".join(["\"" + args.subfolder+ "/" "rwgt_" + str(key) + ".dat\"" for key in rd.keys()] ), card_name=args.cardname, card_dir=args.cardpath, patches_directory=patches_directory, utilities_dir=utilities_dir, plugin_directory=plugin_directory))
            os.system("tar {exclude} -zchvf \"{input_files}\" {rwgt_cards} \"{card_name}\" \"{card_dir}\" \"{patches_directory}\" \"{utilities_dir}\" \"{plugin_directory}\"".format(exclude=exclude_rwgt, input_files=input_files, rwgt_cards=" ".join(["\"" + args.subfolder+ "/" "rwgt_" + str(key) + "_" + args.cardname + ".dat\"" for key in rd.keys()] ), card_name=args.cardname, card_dir=args.cardpath, patches_directory=patches_directory, utilities_dir=utilities_dir, plugin_directory=plugin_directory))


    if any(i in ["sub", "all"] for i in args.task ):

        print(">> Submitting REWEIGHT condor job and wait")

        mkdir("condor_log")

        for key in rd.keys():
            os.system("condor_submit \"{}\" | tail -n1 | rev | cut -d' ' -f1 | rev".format("rwgt_" + str(key) + "_" + args.cardname + ".jdl"))

        #colllecting jobs ids
        out = subprocess.Popen(["condor_q", "-format",  "%d.", "ClusterId", "-format",  "%d\n",  "ProcId"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        all_procs = stdout.split("\n")[:-1]
        this_procs = all_procs[:len(rd.keys())] # the proc we submitted hopefully are the last ones
        print(all_procs)

        if "all" in args.task:

            while(any(i in all_procs for i in this_procs)):

                #querying again the condor scheduler
                out = subprocess.Popen(["condor_q", "-format",  "%d.", "ClusterId", "-format",  "%d\n",  "ProcId"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                stdout,stderr = out.communicate()
                all_procs = stdout.split("\n")[:-1]
                print(all_procs)
                time.sleep(5)
        
        print("---> ALL Jobs Finished")

    if any(i in ["mvoutput", "check", "resub"] for i in args.task ):

        os.chdir(PRODHOME)

        if os.path.isfile("tmp_{}/processed.txt".format(args.cardname)):
            f = open("tmp_{}/processed.txt".format(args.cardname))
            good_proc_ = f.readlines() 
            good_proc = [i.split("\n")[0] for i in good_proc_]
        else:
            good_proc = []

        print("---> Copying output results in tmp dir")
        if not os.path.isdir("tmp_{}".format(args.cardname)):
            mkdir("tmp_{}".format(args.cardname))
        all_outputs = glob("rwgt_*_" + args.cardname + "_output.tar.xz")

        for o in all_outputs:
            ops = o.split("rwgt_")[1].split("_" + args.cardname + "_output.tar.xz")[0]
            #avoid to copy back the tarred files we already know are good
            if "rwgt_{}.tar.xz".format(ops) not in good_proc:
                print("---> Copying {}".format(ops))
                ops = o.split("rwgt_")[1].split("_" + args.cardname + "_output.tar.xz")[0]
                os.system("cp {} tmp_{}/rwgt_{}.tar.xz".format(o, args.cardname, ops))

        #f.close()

    

    if any(i in ["check", "resub"] for i in args.task ):

        os.chdir(PRODHOME)
        if not os.path.isdir("tmp_{}".format(args.cardname)):
            print("[ERROR] No tmp_{} directory....".format(args.cardname))
            sys.exit(0)
        
        os.chdir("tmp_{}".format(args.cardname))
        all_outputs = glob("*.tar.gz".format(args.cardname))

        if os.path.isfile("processed.txt"):
            f = open("processed.txt")
            contents = [i.strip("\n") for i in f.readlines()]
        else:
            contents = []

        f = open("processed.txt".format(args.cardname), "a")

        not_ok = []
        for idx, key in enumerate(rd.keys()):
            
            # if we already know this sample is good we skip
            if "rwgt_"+key+".tar.xz" in contents: 
                continue 


            #else we do the checks

            if not os.path.isfile("rwgt_" + key + ".tar.xz"):
                print("-> Missing " + key)
                not_ok.append(key) 

            else:
                print("--> UnTarring reweight " + "rwgt_" + key + ".tar.xz" + " {:.2f}%".format(100*float(idx)/len(rd.keys())))
                dir_name = "rwgt_" + key
                if os.path.isfile(dir_name): continue     
                os.system("tar axf " + "rwgt_" + key + ".tar.xz")


                if not os.path.isdir("rwgt_" + key + "/rw_me"):
                    print("-> Missing base dir rw_me" + key + " REMOVING FROM TMP")
                    os.system("rm -rf rwgt_" + key + ".tar.xz")
                    not_ok.append(key)
                else:
                    if not os.path.isfile("rwgt_" + key + "/rw_me/rwgt.pkl"):
                        print("-> Missing pickle file for dir rw_me " + key + " REMOVING FROM TMP")
                        os.system("rm -rf rwgt_" + key + ".tar.xz")
                        not_ok.append(key)

                    elif not os.path.isdir("rwgt_" + key + "/rw_me_second") and key not in not_ok:
                        print("-> Missing second dir rw_me_second" + key + " REMOVING FROM TMP")
                        os.system("rm -rf rwgt_" + key + ".tar.xz")
                        not_ok.append(key)

                os.system("rm -rf {}".format(dir_name))
            
            # if we did not append the sample in the not_ok list then the checks are ok and we append this sample
            # to the processed file
            if key not in not_ok:
                f.write("rwgt_"+key+".tar.xz\n")
        
        print("---> Missing {} points".format(len(not_ok)))
        f.close()
        os.chdir(PRODHOME)


    if any(i in ["resub"] for i in args.task ):

        out = subprocess.Popen(["condor_q"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        stdout = stdout.split("\n")

        for k in not_ok:
            
            on_condor = False
            for line in stdout:
                if "rwgt_" + k + "_" + args.cardname + ".sh" in line: 
                    print("---> Reweight point " + k + " is running on condor with id " + str(line.split(" ")[0]))
                    on_condor = True

            if not on_condor: 
                print("Deleting output --> {}".format(k))
                if os.path.isdir("rwgt_{}_".format(k) + args.cardname + "_output.tar.xz"):
                    os.system("rm rwgt_{}_".format(k) + args.cardname + "_output.tar.xz")
                print("Resubmitting --> {}".format(k))
                os.system("condor_submit \"{}\" | tail -n1 | rev | cut -d' ' -f1 | rev".format("rwgt_" + str(k) + "_" + args.cardname + ".jdl"))
        

    if any(i in ["mv", "all"] for i in args.task ):  

        os.chdir(PRODHOME)

        # check if process dir under workdir
        if os.path.isdir(args.cardname + "/" + args.cardname + "_gridpack/work/gridpack") and os.path.isdir(args.cardname + "/" + args.cardname + "_gridpack/work/gridpack/process"):
            if not os.path.isdir(args.cardname + "/" + args.cardname + "_gridpack/work/process"):
                print("--> Moving process directory from gridpack/process under work directory ")
                os.system("mv " + args.cardname + "/" + args.cardname + "_gridpack/work/gridpack/process " + WORKDIR)    

        #check if we unpacked before the end of jobs to check
        is_checked = os.path.isdir("tmp_{}".format(args.cardname))

        #create main rwgt directory if not present in the gridpack directory 
        if not os.path.isdir(args.cardname + "/" + args.cardname + "_gridpack/work/process/madevent/rwgt"):
            mkdir(args.cardname + "/" + args.cardname + "_gridpack/work/process/madevent/rwgt")
        
        all_rwgt_dirs = len(rd.keys())

        for idx, key in enumerate(rd.keys()):
            print("--> Processing reweight rwgt_" + key + " {:.2f}%".format(100*float(idx)/all_rwgt_dirs))

            if is_checked and os.path.isfile("tmp_{}".format(args.cardname) + "/rwgt_" + key + ".tar.xz"): 
                if not os.path.isfile(args.cardname + "/" + args.cardname + "_gridpack/work/process/madevent/rwgt/rwgt_{}.tar.xz".format(key) ):
                    os.system("cp tmp_{}/rwgt_{}.tar.xz ".format(args.cardname, key) + args.cardname + "/" + args.cardname + "_gridpack/work/process/madevent/rwgt")
                else:
                    print("--> Reweight {} already present, skipping".format(key))

            else:
                print("[ERROR]")
                sys.exit(0)

    #############################################

    if any(i in ["prepare", "all"] for i in args.task ):
        
        ############
        os.chdir(WORKDIR)

        if os.path.isdir("gridpack"):
            print("---> Removing previously made gridpack folder")
            os.system("rm -rf gridpack")

        mkdir("gridpack")
        ############

        os.chdir(PRODHOME)

        rwgt = os.path.abspath(args.cardname + "/" + args.cardname + "_gridpack/work/process/madevent/rwgt")
        if not os.path.isdir(rwgt):
            rwgt = os.path.abspath(args.cardname + "/" + args.cardname + "_gridpack/work/gridpack/process/madevent/rwgt")
            if not os.path.isdir(rwgt):
                print("[ERROR] The rwgt directory is not under WORKDIR neither WORKDIR/gridpack")
                sys.exit(0)
        
        os.chdir(rwgt)

        # Now we want to copy both single reweight cards and the 
        # modified script 
        if os.path.isdir("{}/rw_cards".format("/".join(i for i in rwgt.split("/")[:-1]))):
            os.system("rm -rf {}/rw_cards".format("/".join(i for i in rwgt.split("/")[:-1])))

        mkdir("{}/rw_cards".format("/".join(i for i in rwgt.split("/")[:-1])))
        os.system("cp -r {}/*.dat {}/rw_cards".format(os.path.join(PRODHOME, args.subfolder), "/".join(i for i in rwgt.split("/")[:-1])))


        # modify the names so that it is easier to recover from the .sh script
        # e.g. rwgt_cHbox_cHDD_WWjjenumunu -> rwgt_cHbox_cHDD
        l = glob("{}/rw_cards/*".format("/".join(i for i in rwgt.split("/")[:-1])))
        for i in l:
            name = i.split("/")[-1].split("_" + args.cardname + ".dat")[0] + ".dat"
            path = "{}/rw_cards/".format("/".join(i for i in rwgt.split("/")[:-1])) + name
            os.system("mv {} {}".format(i, path))

        print("COPIO NUOVI SCRIPT")
        # Copying the new script into this directory 
        os.system("cp {} {}".format(os.path.join(PRODHOME, "runcmsgrid_LO_tar.sh"), os.path.join(WORKDIR, "gridpack/runcmsgrid_LO_tar.sh")))


        os.chdir(os.path.join(WORKDIR, "gridpack"))

        os.system("ls")

        os.system("sed -i s/SCRAM_ARCH_VERSION_REPLACE/{}/g runcmsgrid_LO_tar.sh".format(scram_arch))
        os.system("sed -i s/CMSSW_VERSION_REPLACE/{}/g runcmsgrid_LO_tar.sh".format(cmssw_version))
        
        pdfExtraArgs=""

        if args.is5FlavorScheme:
            pdfExtraArgs+="--is5FlavorScheme"
        
        print("---> Retrieve pdf for {} flavour scheme".format(5 if args.is5FlavorScheme else 4))

        out = subprocess.Popen(["python", "{}/getMG5_aMC_PDFInputs.py".format(script_dir),  "-f",  "systematics", "-c",  "2017", "{}".format(pdfExtraArgs)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pdfSysArgs,stderr = out.communicate()

        os.system("sed -i s/PDF_SETS_REPLACE/{pdfSysArgs}/g runcmsgrid_LO_tar.sh".format(pdfSysArgs=pdfSysArgs[:-1]))

        os.system("ls")

        ########

        print("---> Preparing final gridpack")
        os.chdir(PRODHOME + "/" + args.cardname + "/" + args.cardname + "_gridpack/work/process")
        os.system("echo \"mg5_path = ../../mgbasedir\" >> ./madevent/Cards/me5_configuration.txt")
        os.system("echo \"cluster_temp_path = None\" >> ./madevent/Cards/me5_configuration.txt")
        os.system("echo \"run_mode = 0\" >> ./madevent/Cards/me5_configuration.txt")

        os.chdir(WORKDIR)


        print("---> Move process directory into gridpack/process")
        # mv is hundreds of time quicker than cp
        os.system("mv process gridpack/process")

        print("---> Copy Madgraph into gridpack/mgbasedir")
        os.system("cp -a {}/ gridpack/mgbasedir".format(MGBASEDIRORIG))
            

        os.chdir("gridpack")
        print("---> Copy runcmsgrid_LO.sh into gridpack/runcmsgrid.sh")
        os.system("cp {}/runcmsgrid_LO.sh ./runcmsgrid.sh".format(PRODHOME))

        os.system("sed -i s/SCRAM_ARCH_VERSION_REPLACE/{}/g runcmsgrid.sh".format(scram_arch))
        os.system("sed -i s/CMSSW_VERSION_REPLACE/{}/g runcmsgrid.sh".format(cmssw_version))
        
        pdfExtraArgs=""

        if args.is5FlavorScheme:
            pdfExtraArgs+="--is5FlavorScheme"
        
        print("---> Retrieve pdf for {} flavour scheme".format(5 if args.is5FlavorScheme else 4))

        out = subprocess.Popen(["python", "{}/getMG5_aMC_PDFInputs.py".format(script_dir),  "-f",  "systematics", "-c",  "2017", "{}".format(pdfExtraArgs)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pdfSysArgs,stderr = out.communicate()

        os.system("sed -i s/PDF_SETS_REPLACE/{pdfSysArgs}/g runcmsgrid.sh".format(pdfSysArgs=pdfSysArgs[:-1]))

        print("---> Clean unneeded files for generation")
        #clean unneeded files for generation
        os.system("{helpers_dir}/cleangridmore.sh".format(helpers_dir=helpers_dir))

        # copy merge.pl from Utilities to allow merging LO events
        print("---> Copy merge.pl from Utilities to allow merging LO events")
        os.chdir("{}/gridpack".format(WORKDIR))
        os.system("cp {}/Utilities/merge.pl .".format(PRODHOME))

        if args.createreweight:
            print("---> Creating custom reweight card and copy it in cards folder and gridpack/process/madevent/Cards/reweight_card.dat")
            os.chdir(PRODHOME)
            build_reweight_card(rd, args.change_process, [args.cardpath + "/" + args.cardname + "_reweight_card.dat", WORKDIR + "/gridpack/process/madevent/Cards/reweight_card.dat"])
    


    if any(i in ["rwgtcard"] for i in args.task ):
        os.chdir(PRODHOME)
        build_reweight_card(rd, args.change_process, [args.cardpath + "/" + args.cardname + "_reweight_card.dat", WORKDIR + "/gridpack/process/madevent/Cards/reweight_card.dat"])

    
    if any(i in ["compress", "all"] for i in args.task ):

        if not os.path.isdir(args.cardname + "/" + args.cardname + "_gridpack/work/gridpack/process"):
            if os.path.isdir(args.cardname + "/" + args.cardname + "_gridpack/work/process"):
                os.system("mv " + args.cardname + "/" + args.cardname + "_gridpack/work/process " + args.cardname + "/" + args.cardname + "_gridpack/work/gridpack/process")
            else:
                sys.exit("[ERROR] can't find priocess dir")

        #Finishing the gridpack
        os.chdir("{}/gridpack".format(WORKDIR))
        make_tarball(WORKDIR, args.iscmsconnect, PRODHOME, CARDSDIR, args.cardname, scram_arch, cmssw_version)


    if any(i in ["clean"] for i in args.task ):

        for key in rd.keys():
            os.system("rm rwgt_" + str(key)+ "_" + args.cardname + ".sh")
            os.system("rm rwgt_" + str(key)+ "_" + args.cardname + ".jdl")
            os.system("rm rwgt_" + str(key)+ "_" + args.cardname + ".log")
            os.system("rm rwgt_" + str(key) + "_" + args.cardname + "_output.tar.xz")
            os.system("rm -rf " + args.subfolder)

    ##################################
    ##################################
    ##################################
    ##################################
    ##################################
    ##################################

    if any(i in ["createsymlinks"] for i in args.task ):
        
        rwgt = os.path.join(PRODHOME, "tmp_{}".format(args.cardname))
        if not os.path.isdir(rwgt): 
            print("[ERROR] Before creating symbolic links to rw_me, run check")
            sys.exit(0)

        os.chdir(rwgt)
        all_rwgts = glob("*")

        all_rw_me = glob("*/rw_me")
        if len(all_rw_me) == 0:
            print("[ERROR] You first need to unpack tmp directory. -t unpacktmp")
            sys.exit(0)

        basesize = get_folder_size(all_rw_me[0])
        for i in all_rw_me[1:]:
            if get_folder_size(i) != basesize: 
                print("[ERROR] folder {} does not match basefolder size: {},  {}...".format(i, get_folder_size(i), basesize))
                #sys.exit(0)


        # Take first rwgt directory in the list. Save the SM ME (rw_me) also for all the
        # other reweight points. 
        # Remember, the script will exit if rw_me cointains the rwgt.pkl file to avoid things getting lost or
        # overwritten
        for idx, j in enumerate(all_rwgts):
            if os.path.isdir(j + "/rw_me"):

                #save the index of the benchmark directory along with 
                # the relative path of the rw_me directory.
                # relative so that when we tar the symbolic links will remain
                orig_rw_me = [idx, "../" + j + "/rw_me" ]
                break 

        sed_rwgt_interface = False
        for idx, rwgt_dir in enumerate(all_rwgts):

            print("---> Create symlinks to rw_me for {} {:.2f}%".format(rwgt_dir, 100*float(idx)/(len(all_rwgts)-1)))

            os.chdir(rwgt_dir)

            if os.path.isfile("rw_me/rwgt.pkl"): 
                print("[INFO] rwgt.pkl is under rw_me, this step assumes rwgt.pkl under rw_me_second ... MOVING")
                os.system("mv rw_me/rwgt.pkl rw_me_second")
                sed_rwgt_interface = True
                #sys.exit(0)

            # do not create symlink if the index is equal to the 
            # original designated rw directory 
            if idx == orig_rw_me[0]: 
                os.chdir(rwgt)
                continue
            
            if not os.path.islink("rw_me"):
                print("--> Removing")
                os.system("rm -rf rw_me")
                os.system("ln -s {} rw_me".format(orig_rw_me[1]))
            else:
                print("---> Symlink for rw_me already present")
                # if there is a symlink this procedure was already done, so we specifiy 
                # that the script should change the path to pick up the pickles from rw_me to rw_me_second
                sed_rwgt_interface = True

            os.chdir(rwgt)

        # check whether a gridpack folder is already present
        # otherwise we sed the appropriate mmgdir

        mg = os.path.join(WORKDIR, "gridpack/mgbasedir" )
        if not os.path.isdir(mg):
            mg = os.path.join(WORKDIR, MGBASEDIRORIG)
            if not os.path.isdir(mg):
                print("[ERROR] No MG dir found under {}".format(mg))

        

        # So if we found that pkls files are saved in rw_me directory 
        # we assume that the reweight interface of madgraph will search pickles 
        # in rw_me. We change that to rw_me_second in functions do_launch and load_from_pickle
        if sed_rwgt_interface:
            os.chdir(WORKDIR)
            os.system("sed -i s/\"self.rwgt_dir,\'rw_me\',\'rwgt.pkl\'\"/\"self.rwgt_dir,\'rw_me_second\',\'rwgt.pkl\'\"/g {}".format(os.path.join(mg, "madgraph/interface/reweight_interface.py")))
            os.system("sed -i s/\"self.rwgt_dir, \'rw_me\', \'rwgt.pkl\'\"/\"self.rwgt_dir,\'rw_me_second\',\'rwgt.pkl\'\"/g {}".format(os.path.join(mg, "madgraph/interface/reweight_interface.py")))


    if any(i in ["tarrwgt"] for i in args.task ):
        rwgt = os.path.abspath(args.cardname + "/" + args.cardname + "_gridpack/work/process/madevent/rwgt")
        if not os.path.isdir(rwgt):
            rwgt = os.path.abspath(args.cardname + "/" + args.cardname + "_gridpack/work/gridpack/process/madevent/rwgt")
            if not os.path.isdir(rwgt):
                print("[ERROR] The rwgt directory is not under WORKDIR neither WORKDIR/gridpack")
                sys.exit(0)
        
        os.chdir(rwgt)
        ls = glob("*/")

        # check wether we run createsymlinks before:
        createsyml = False 
        for dir_ in ls:
            if os.path.islink(dir_ + "/rw_me"): 
                createsyml = True
                break 

        # If we run the symlink than we do not want to tar the 
        # intial directory so that the reweighting will always find the 
        # initial point (pointing to rw_me)
        original = ""
        if createsyml:
            for dir_ in ls:
                if not os.path.islink(dir_ + "/rw_me") and os.path.isdir(dir_ + "/rw_me"):
                    original = dir_ 

        if original == "" and createsyml: 
            print("[ERROR] Could not find original rw_me directory (the non symbolic link). Check what's happening...")
            sys.exit(0)


        print("---> Tarring single reweight directories and send new running script / single reweight cards ...")


        os.chdir(rwgt)
        for idx, i in enumerate(ls):
            print("--> Processing reweight " + i + " {:.2f}%".format(100*float(idx)/len(ls)))
            if os.path.isfile("{}.tar.gz".format(i[:-1])): 
                print("it's a file")
                continue
            # if this is the original rwgt directory then we do not tar it
            # so it will always be available 
            if i == original: continue

            os.system("XZ_OPT=\"--lzma2=preset=9,dict=512MiB\" tar -cJpsf {}.tar.gz {}".format(i[:-1], i[:-1]))

            #removing the dir to actually save space
            os.system("rm -rf {}".format(i))

        # Now we want to copy both single reweight cards and the 
        # modified script 
        if os.path.isdir("{}/rw_cards".format("/".join(i for i in rwgt.split("/")[:-1]))):
            os.system("rm -rf {}/rw_cards".format("/".join(i for i in rwgt.split("/")[:-1])))

        mkdir("{}/rw_cards".format("/".join(i for i in rwgt.split("/")[:-1])))
        os.system("cp -r {}/*.dat {}/rw_cards".format(os.path.join(PRODHOME, args.subfolder), "/".join(i for i in rwgt.split("/")[:-1])))


        # modify the names so that it is easier to recover from the .sh script
        # e.g. rwgt_cHbox_cHDD_WWjjenumunu -> rwgt_cHbox_cHDD
        l = glob("{}/rw_cards/*".format("/".join(i for i in rwgt.split("/")[:-1])))
        for i in l:
            name = i.split("/")[-1].split("_" + args.cardname + ".dat")[0] + ".dat"
            path = "{}/rw_cards/".format("/".join(i for i in rwgt.split("/")[:-1])) + name
            os.system("mv {} {}".format(i, path))


        # os.system("cp {} {}".format(os.path.join(PRODHOME, "runcmsgrid_LO_tar.sh"), "/".join(WORKDIR, "gridpack/runcmsgrid.sh")))

        # os.chdir(os.path.join(WORKDIR, "gridpack"))

        # os.system("sed -i s/SCRAM_ARCH_VERSION_REPLACE/{}/g runcmsgrid.sh".format(scram_arch))
        # os.system("sed -i s/CMSSW_VERSION_REPLACE/{}/g runcmsgrid.sh".format(cmssw_version))
        
        # pdfExtraArgs=""

        # if args.is5FlavorScheme:
        #     pdfExtraArgs+="--is5FlavorScheme"
        
        # print("---> Retrieve pdf for {} flavour scheme".format(5 if args.is5FlavorScheme else 4))

        # out = subprocess.Popen(["python", "{}/getMG5_aMC_PDFInputs.py".format(script_dir),  "-f",  "systematics", "-c",  "2017", "{}".format(pdfExtraArgs)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # pdfSysArgs,stderr = out.communicate()

        # os.system("sed -i s/PDF_SETS_REPLACE/{pdfSysArgs}/g runcmsgrid.sh".format(pdfSysArgs=pdfSysArgs[:-1]))

        os.system("cp {} {}".format(os.path.join(PRODHOME, "runcmsgrid_LO_tar.sh"), os.path.join(WORKDIR, "gridpack/runcmsgrid_LO_tar.sh")))

        os.chdir(os.path.join(WORKDIR, "gridpack"))

        os.system("sed -i s/SCRAM_ARCH_VERSION_REPLACE/{}/g runcmsgrid_LO_tar.sh".format(scram_arch))
        os.system("sed -i s/CMSSW_VERSION_REPLACE/{}/g runcmsgrid_LO_tar.sh".format(cmssw_version))
        
        pdfExtraArgs=""

        if args.is5FlavorScheme:
            pdfExtraArgs+="--is5FlavorScheme"
        
        print("---> Retrieve pdf for {} flavour scheme".format(5 if args.is5FlavorScheme else 4))

        out = subprocess.Popen(["python", "{}/getMG5_aMC_PDFInputs.py".format(script_dir),  "-f",  "systematics", "-c",  "2017", "{}".format(pdfExtraArgs)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pdfSysArgs,stderr = out.communicate()

        os.system("sed -i s/PDF_SETS_REPLACE/{pdfSysArgs}/g runcmsgrid_LO_tar.sh".format(pdfSysArgs=pdfSysArgs[:-1]))


    print("--> Done <---")

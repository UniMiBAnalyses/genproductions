# genproductions
Generator fragments for MC production

The package includes the datacards used for various generators inclusing POWHEG, MG5_aMC@NLO, Sherpa, Phantom, Pythia...

Further details are reported in the twiki: https://twiki.cern.ch/twiki/bin/view/CMS/GeneratorMain#How_to_produce_gridpacks

Instructions on how to use the fragments are here https://twiki.cern.ch/twiki/bin/view/CMS/GitRepositoryForGenProduction

# Unimib EFT gridpack production

This repo contains centrall tools to produce gridpacks (genprocutions) along with custom EFT tools to produce EFT gridpacks with SMEFTsim.

# Gridpacks

A MG folder which has been optimised for batch-mode computation. The MadGraph "single-diagrams-enhanched multichannel" integration technique makes it possible to split the phase space integration into small bits that can be evaluated independently. The expolitation of a fully parallel compututational workflow allows to reduce the time required to obtain a MG folder by order of magnitudes.
MG gridpack computation is split in two(three) steps: CODEGEN, INTEGRATE (MADSPIN), where madspin is not mandatory. 
- CODEGEN: code generation step, finds processes / subprocesses and diagrams
- INTEGRATE: phase space integration
- MADSPIN: decay of particles accounting for spin, offshell eccets, ...

# Generate gridpacks with EFT contributions
## SMEFTsim compressed UFO

EFT contributions are simulated at LO via SMEFTsim (https://smeftsim.github.io/).
A ready-to-go version of SMEFTsim UFO model with U35 flavour scheme and mW,mZ,Gf input scheme is publicly accessible at http://gboldrin.web.cern.ch/gboldrin/generators/SMEFTsim_U35_MwScheme_UFO.tar.gz 
This version is up to date as of 8th November 2021 and also contains restriction cards for 15 operators (cW,cHW,cHbox,cHDD,cHWB,cHl1,cHl3,cHq1,cHq3,cll,cll1,cqq1,cqq3,cqq11,cqq31) both for single insertion or for all the posssible pairs. The directory also contain custom restriction cards to activate all operators at the same time or a subset of them e.g. http://gboldrin.web.cern.ch/gboldrin/generators/restrict_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_massless.dat	

If you need a more up to date version of SMEFTsim or different restriction cards, it is highly suggested to clone a copy of SMEFTsim, build the restrictions you need, move them under the UFO model, pack everything again and copy the compressed folder on your web area (e.g. /eos/user/y/yourusername/www on lxplus).

- Create a tar version of SMEFTsim with restriction cards

```
git clone git@github.com:SMEFTsim/SMEFTsim.git
mv SMEFTsim/UFO_models/SMEFTsim_MFV_alphaScheme_UFO . # choose the UFO model you need
cp SMEFTsim_MFV_alphaScheme_UFO/restrict_SMlimit_massless.dat restrict_your_set_of_op_massless.dat #copy SM restriction 
#Modify restrict_your_set_of_op_massless.dat turning on and off operators under SMEFT or SMEFTFV blocks (on = 9.999999e-01, off = 0)
tar -zcvf SMEFTsim_MFV_alphaScheme_UFO.tar.gz SMEFTsim_MFV_alphaScheme_UFO
xrdcp SMEFTsim_MFV_alphaScheme_UFO.tar.gz /eos/user/y/yourusername/www
```

Examples of restriction cards (and script to automate the cards generation) can be found at https://github.com/UniMiBAnalyses/D6EFTStudies/tree/master/madgraph_model/v3_0 (https://github.com/UniMiBAnalyses/D6EFTStudies/blob/master/madgraph_model/buildRestrict_v3_0.py)


## Lxplus or CMSConnect

Gridpack generation can be done both on lxplus or cmsconnect as both have HTCondor to submit batch jobs. However, part of the gridpack will still run in local.
A lxplus worker node has 10 cores while cmsconnect has 48. You will be 5 times quicker while working on cmsconnect than lxplus.
Some comments:
- Never work fully local on cmsconnect. If you overload the system your jobs will be killed (e.g. if you submit multiple gridpacks creation in parallel).
- You can work fully local on lxplus, at least, you will hardly find resource issues.

Follow this tutorial on how to subscribe to cmsconnect:
https://indico.cern.ch/event/615524/contributions/2520456/attachments/1430441/2197104/March20_2017_gen_meeting.pdf

## EFT gridpack submission scripts overview and clarifications

Once you decided if you'll generate your MG gridpack on lxplus or cmsconnect, simply login, go to the desired working folder and clone this repo (check if this repo is up to date). If needed, change branch but scripts only work for master as of 8/11/2021:

```
git clone git@github.com:UniMiBAnalyses/genproductions.git && cd genproductions/bin/MadGraph5_aMCatNLO/

```

The main script is: `gridpack_generation_EFT.sh` which is a copy of `gridpack_generation.sh` with some lines added to it:

```
245       wget --no-check-certificate http://gboldrin.web.cern.ch/gboldrin/generators/SMEFTsim_U35_MwScheme_UFO.tar.gz
246       cd models
247       tar xavf ../SMEFTsim_U35_MwScheme_UFO.tar.gz
248       cd SMEFTsim_U35_MwScheme_UFO
249       # wget all restrictions
250       wget --no-check-certificate http://gboldrin.web.cern.ch/gboldrin/generators/restrict_cHWB_cHDD_cHl1_cHl3_cHq1_cHq3_cll_cll1_massless.dat
251       wget --no-check-certificate http://gboldrin.web.cern.ch/gboldrin/generators/restrict_cW_cHWB_cHDD_cHl1_cHl3_cHq1_cHq3_cll_cll1_massless.dat
252       wget --no-check-certificate http://gboldrin.web.cern.ch/gboldrin/generators/restrict_cW_cHWB_cHDD_cll1_cHl1_cHl3_cHq1_cHq3_massless.dat
253       wget --no-check-certificate http://gboldrin.web.cern.ch/gboldrin/generators/restrict_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_massless.dat
254       cd ../.. 
```

If you need to generate from a different branch than master as of 8/11/2021, simply copy `gridpack_generation.sh` and add those lines. If you genrated your version of compressed SMEFTsim UFO model, simply replace this paths with yours.

Accessory scripts needs to be modified in order to run `gridpack_generation_EFT.sh` on condor: `submit_cmsconnect_gridpack_generation_EFT.sh`, `submit_condor_gridpack_generation_EFT.sh`. 
These are just copies of the same ones without `_EFT`suffix and few lines modified. If you need to work on another branch and not master as of 8/11/2021, simply copy `submit_cmsconnect_gridpack_generation.sh`, `submit_condor_gridpack_generation.sh` and replace `gridpack_generation.sh` with `gridpack_generation_EFT.sh` everywhere.


## Generate the gridpack

Once you have all necessary scripts you are ready to issue the generation:

```
./gridpack_generation_EFT.sh card_name path/to/cards # this runs locally 
```

Where path/to/cards contains the MG5 cards. Some are mandatory and must follow a naming convention: `card_name_proc_card.dat`, `card_name_run_card.dat`.
An accessory card will be needed for SMEFTsim: `card_name_customizecards.dat`, where you set the initial values for EFT coupling.
An additional card is mandatory if one want to use the reweight module: `card_name_reweight_card.dat`. 
**IMPORTANT**: You do not need an extramodel card, the script will always download the SMEFTsim tarball even if you won't need it.

Example of cards can be found under:

`cards/ZZ2e2mu/ZZ2e2mu_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_SM_LI_QU_IN`

Where we generate a VBS ZZ process into 4 leptons of different flavour (2e, 2mu) with EFT contributions from 15 operators. We also use the reweight module to change hypothesis and turn off-on operators.

Following the ZZ example:
```
./gridpack_generation_EFT.sh ZZ2e2mu_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_SM_LI_QU_IN cards/ZZ2e2mu/ZZ2e2mu_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_SM_LI_QU_IN # this runs locally, should be avoided 

./submit_cmsconnect_gridpack_generation.sh ZZ2e2mu_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_SM_LI_QU_IN cards/ZZ2e2mu/ZZ2e2mu_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_SM_LI_QU_IN (n_cores) ("memory")

./submit_condor_gridpack_generation.sh ZZ2e2mu_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_SM_LI_QU_IN cards/ZZ2e2mu/ZZ2e2mu_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_SM_LI_QU_IN (n_cores) ("memory")
```

Why is it highly suggested to generate through condor? You will be able to generate a gridpack ~ 10 times faster as the INTEGRATE step will be submitted to various worker node via condor.

As an example, a gridpack on cmsconnect running locally will be ablle to execute 48 jobs simultaneously (Idle means job waiting to be run)

```
INFO:  Idle: 613,  Running: 48,  Completed: 535 [  73h 49m  ] # the INTEGRATE steps has been running for ~ 3 days, and 3 days approx. left
```

Different gridpack but with batch submission:

```
INFO:  Idle: 0,  Running: 423,  Completed: 179 [  3m 19s  ]
```

You can see that condor submission can handle >10 times simultaneous jobs that local generation (and your jobs won't be centrally killed by cmsconnect mainteiners as you won't overload the machines).

## Sumbit the reweight step on condor

This branch cloned from genproduction was built to parallelize the reweight step on condor nodes. This comes useful when the initial matrix element is so big in term of memory consumption that the reweighting step (which runs locally) will fail on local machines with limited amount of resources. Also the parallelisation come at hand when the reweight point might differ from the integration ones (e.g. starting CODEGEN and INTEGRATE from SM and reweight to EFT space). For example you generate CODEGEN from $cW$ and reweight to all possible operators of the Warsaw basis which result in thousands of reweight points impossible to compute serially (remember that if the stgarting phase space is significantly different from the reweight one this method is not guaranteed to close and you should always compare the results with a benchmark scenario for example predictions from Amplitude Decomposition ).

In order to do that a script ```submit_reweight_on_condor.py``` is provided.

In the cards folder, as stated in previous points, you need to create a process card and a run card ```<proc_name_proc_card.dat``` and ```<proc_name_run_card.dat``` . Do not specify any reweight card at this point.

Run the gridpack generation as usual for CODEGEN and INTEGRATE:

```
./submit_cmsconnect_gridpack_generation.sh <proc_name> <cards_path> ...
```

Upon completion you should see the follwoing message: ```gridpack_generation_EFT.sh: line 937: REWEIGHT_ON_CONDOR: unbound variable```
It is an error message which prevents the creation of the gridpack tarball and allows us to run the reweight step from the output of CODEGEN and INTEGRATE.

Open the file ```operators.py``` and specify the operators you want to reweight on by specifying the operator number in this list:
https://github.com/UniMiBAnalyses/genproductions/blob/WV_semilep_EFT/bin/MadGraph5_aMCatNLO/operators.py#L3

Then run the ```sumit_reweight_on_condor.py``` script. It supports different command line arguments:

```
python submit_reweight_on_condor.py --h

optional arguments:
  -h, --help            show this help message and exit
  -cn CARDNAME, --cardname CARDNAME
                        The name of the cards, <name>_proc_card.dat
  -cp CARDPATH, --cardpath CARDPATH
                        The path to the cards directory
  -t TASK [TASK ...], --task TASK [TASK ...]
                        Tasks to be executed (separated by a space). Default
                        is all. Can choose between: rew (only write rew cards
                        and execs), tar (Create tarball of input gridpack),
                        sub (submit all jobs), mv (move all results once jobs
                        are finished in the right position), clean (clean all
                        files created that are not useful), prepare (prepare
                        final gridpack, set of sed and paths), compress
                        (create the final gridpack) createsymlink (rw_me
                        directories are a waste of space. Just retain one and
                        create sym links to the first)
  -sf SUBFOLDER, --subfolder SUBFOLDER
                        The path to the folder where .jid, exec and reweight
                        cards will be saved
  -is5f, --is5FlavorScheme
                        Is the gridpack intended for 5fs? Default is true
  -scram SCRAMARCH, --scramarch SCRAMARCH
                        Scram arch version required. Default is
                        slc7_amd64_gcc700
  -cmssw CMSSW, --cmssw CMSSW
                        CMSSW version required. Default is CMSSW_10_6_19
  -iscmsc, --iscmsconnect
                        Are you working on cmsconnect? Default is true
  -cr, --createreweight
                        File operator.py will be imported and restriction
                        cards created
  -change_process CHANGE_PROCESS, --change_process CHANGE_PROCESS
                        If args.cr is specified, add this to change process in
                        reweight card
  -m MODEL, --model MODEL
                        If args.cr is specified, add this to change the
                        baseline model. Default is
                        SMEFTsim_topU3l_MwScheme_UFO_b_massless
  -appendsm, --appendsm
                        If turned on at reweight point also SMlimit massless
                       model will be imported and weight computed
```


```-cn``` and ```-cp``` arguments are the same ones you specified when running ```./submit_cmsconnect_gridpack_generation.sh``` scripts. ```-sf``` is the path to a subfolder (if does not exist it will be created) that will store the condor files needed for submission. All the other points are self-expllanatory and usually will be set by default arguments to a reasonable value. Be sure that the flavour scheme, cmssw version and scram arch versions follow your prerequisites. The argument ```-iscmsc``` differentiates the gridpack generation on cmsconnect and lxplus (some paths / configuration differ between the two so be sure to be consistent). The argument ```-cr``` will automatically create all necessary reweight cards to be run on condor nodes for a particular reweight point (c=+1, c=-1, SM, c1=1 c2=1), if you want to select ad hoc values for reweight points you have to modify yourself the script. ```-appendsm``` will also add a condor job for the SM hypothesis importing the restriction ```restrict_SM_limit_massless.dat```. If you started the CODEGEN and INTEGRATE from SM point (e.g. ```generate p p > l+ l- QCD=0 NP=0```) you will need to change the process definition to allow EFT insertion (```NP=0``` should be converted in ```NP=1,2,3,...```). The argument ```-change_process``` allows the user to do that. If the process foresee an additional lines (e.g. from proc card ```generate p p > w+ \n add process p p > w-```) you can split the lines separating with a comma (e.g. ```-change_process "change process p p > w+ NP=1", "add process p p > w- NP=1"```. The argument ```-m``` lets you change the model from initial hypothesis.

The argument `-t` specifies the task you want to execute. The script is modular so you can check the output at each stage.
The logical order of the tasks is the following: 

- Create reweight card and condor submit files: ```-t rew```
- Tar the output of CODEGEN + INTEGRATE with reweight card: ```-t tar```
- Submit condor jobs: ```-t sub```
- Check the output of jobs and print unfinished / failed jobs: ```-t check```
- Resubmit failed jobs (ignore jobs running): ```-t resub```
- Move all reweight outputs to the appropriate directory inside gridpack folder: ```-t mv```
- Prepare the gridpack, export paths, create merge files for matching/merging etc. : ```-t prepare```
- Compress the gridpack into the usual tarball: ```-t compress```
- Clean all files created during the process: ```-t clean```

An examples worflow would be:

```
python submit_reweight_on_condor.py -cn emVjj_ewk_dim6 -cp cards/emVjj -sf condor_sub_emVjj -cr  -t rew -appendsm -iscmsc
```

So the script expects a folder with two cards in the following location: ```cards/emVjj/emVjj_ewk_dim6_proc_card.dat```, ```cards/emVjj/emVjj_ewk_dim6_run_card.dat```, the gridpack in the current directory named ```emVjj_ewk_dim6``` containing two subfolders (output of CODEGEN and INTEGRATE): ```emVjj_ewk_dim6_gridpack  emVjj_ewk_dim6_output.tar.xz```.
The script will generate a nerw folder named ```condor_sub_emVjj``` with a bunh of ```.sh, .jdl``` files with  self-explanatory names connecting the process definition and the operators you selected and the reweight card. Inspect the reweight card to check that everything behaves correctly. It will assume 5 flavour scheme, CMSSW=CMSSW_10_6_19, SCRAMARCH=slc7_amd64_gcc700. It will also generate the SM reweight point.

The execution proceeds as follows:
```
python submit_reweight_on_condor.py -cn emVjj_ewk_dim6 -cp cards/emVjj -sf condor_sub_emVjj -cr  -t tar -appendsm -iscmsc
python submit_reweight_on_condor.py -cn emVjj_ewk_dim6 -cp cards/emVjj -sf condor_sub_emVjj -cr  -t sub -appendsm -iscmsc
python submit_reweight_on_condor.py -cn emVjj_ewk_dim6 -cp cards/emVjj -sf condor_sub_emVjj -cr  -t check -appendsm -iscmsc # this should be executed until completion of jobs
# python submit_reweight_on_condor.py -cn emVjj_ewk_dim6 -cp cards/emVjj -sf condor_sub_emVjj -cr  -t resub -appendsm -iscmsc # only in case of errors
python submit_reweight_on_condor.py -cn emVjj_ewk_dim6 -cp cards/emVjj -sf condor_sub_emVjj -cr  -t mv prepare -appendsm -iscmsc
python submit_reweight_on_condor.py -cn emVjj_ewk_dim6 -cp cards/emVjj -sf condor_sub_emVjj -cr  -t compress -appendsm -iscmsc
python submit_reweight_on_condor.py -cn emVjj_ewk_dim6 -cp cards/emVjj -sf condor_sub_emVjj -cr  -t clean -appendsm -iscmsc
```


Further informations can be found in this slides including other practical examples:

https://indico.cern.ch/event/1175148/contributions/4935576/attachments/2474559/4246168/Boldrini_PHGen_04072022.pdf



## Screen (or tmux)

Gridpacks usually take from O(h) to O(days) to be completed. It is unfeasible to stay connected for such a long time length. Screen (or tmux) are essential tools in order to issue commands and leave it running also after disconnecting from the ssh tunnel. Both lxplus and cmsconnect provide out of the box screen support:

```
screen # open a new scren session
screen -ls # list all open screen sessions on the worker node
screen -rD _ID_ # connect to a detached screen session with id = _ID_
```

After issuing the `screen` command a new shell will be opened. You can use it the same way as a normal terminal session. In order to detach from the screen session type `Ctrl + A + D`. You will be redirected to the shell in which the `screen`command wa issued and you can inspect the opened screen session:

```
[gboldrin@lxplus731 MadGraph5_aMCatNLO]$ screen -ls
There is a screen on:
	9358.pts-12.lxplus731	(Detached)
1 Socket in /var/run/screen/S-gboldrin.
```

`9358` is the session ID. To reconnect:

```
screen -rD 9358
screen -rD 9358.pts-12.lxplus731
```

**WARNING**:

There some differences between lxplus and cmsconnect regarding screen. On lxplus you usually log into a worker node (from the example above 731 machine) while on cmsconnect there is only one machine. If you open a screen session on lxplus and then detach from it and log out from the ssh, you'll need to store the machine number and reconnect to the same machine in order to retrive the screen session. From the example above:

```
ssh username@lxplus731.cern.ch
screen -rD 9358
```

Furthermore, the screen session on lxplus works with kerberos tokens which allow the session to have permission to write/read from your afs area. These tickets are created with the command `kinit` and authorised with your lxplus login password. The tickets last for 25 hours after ssh disconnection and there is no way to change that. After 25h the commands won't be able to, for example, read or create files in your user area.

One way to create a persistent screen session on lxplus is to create a keytab which automatically refresh your expired tickets.

From a private folder on your afs (e.g. `/afs/cern.ch/user/u/username/private`) type:

```
mkdir ktokens && ktutil
```

A new prompt will appear. Type in the prompt the following lines:

```
add_entry -password -p USERNAME@CERN.CH -k 1 -e arcfour-hmac-md5
add_entry -password -p USERNAME@CERN.CH -k 1 -e aes256-cts
wkt USERNAME.keytab
Ctrl+D #close ktutil session
```

`k5reauth` can now be used, it will issue user defined commands in a child process and will renew your kerberos tokes after N seconds also for the child itself.

Using the ZZ VBS example, this command will create a permanent screen session with renewable tokens once every 3600 seconds:

```
cd /path/to/genproductions/bin/MadGraph5_aMCatNLO/
k5reauth -f -i 3600 -p USERNAME -k /afs/cern.ch/user/u/username/private/ktokens/USERNAME.keytab -- screen ./submit_cmsconnect_gridpack_generation.sh ZZ2e2mu_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_SM_LI_QU_IN cards/ZZ2e2mu/ZZ2e2mu_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_SM_LI_QU_IN
```

You can also create an alias for this command in your `.bash_profile` or `.bashrc`

```
kscreen(){
    if [[ -z "$1" ]]; then #if no argument passed
        echo "First argument must be the executable name"
    else #pass the argument to screen
        k5reauth -f -i 3600 -p USERNAME -k /afs/cern.ch/user/u/username/private/ktokens/USERNAME.keytab  -- screen $1
    fi
}
```

and use it as a normal screen session:

`
kscreen ./submit_cmsconnect_gridpack_generation.sh ZZ2e2mu_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_SM_LI_QU_IN cards/ZZ2e2mu/ZZ2e2mu_cW_cHWB_cHDD_cHbox_cHW_cHl1_cHl3_cHq1_cHq3_cqq1_cqq11_cqq31_cqq3_cll_cll1_SM_LI_QU_IN
`

# Resubmitting Gridpacks 

Suppose your codegen sstep run fine but something broke at Integration. You do not need to run everything again. You'll have a folder named as your `<card_name>`
with two subfolders: `<card_name>/<card_name>_gridpack`and `<card_name>/<card_name>_output.tar.xz` . To resubmit some step both on local or condor:

```
source Utilities/cmsconnect_utils.sh
source Utilities/source_condor.sh

cd <card_name>
rm -rf <card_name>_gridpack 
cmssw_setup <card_name>_output.tar.xz; cd ..
iscmsconnect=1 bash -x gridpack_generation_EFT.sh ${card_name} ${card_dir} ${workqueue} INTEGRATE ${scram_arch} ${cmssw_version}
```

For example the last line can be issued on condor as:

```
iscmsconnect=1 bash -x gridpack_generation_EFT.sh <card_name> <card_dir> condor INTEGRATE
```

# Integrate Compilation errors for very large EFT gridpacks

It may happen that after the codegen step your EFT gridpack breaks at the pilot run with some cryptic compilation error. This may be due to an error problem as MGv2_6_5 is not design to exploit the full RAM of the node but it is limited. To unlock this limitation and resubmit successfully follow the steps of the chapter "Resubmitting Gridpacks" up to the line `cmssw_setup <card_name>_output.tar.xz`. This command will untar the codegen output and create a `<card_name>_gridpack` folder. Now issue 

```
cd <card_name>_gridpack/work/<card_name>
``` 

you will see a MG folder e.g.

```
ls WmTo2JZto2L_dim6_ewk/WmTo2JZto2L_dim6_ewk_gridpack/work/WmTo2JZto2L_dim6_ewk
Cards  Events  HTML  MGMEVersion.txt  README  README.systematics  Source  SubProcesses	TemplateVersion.txt  bin  index.html  lib  madevent.tar.gz
```

Issue the command

```
sed -i.bak '/FFLAGS= -O -w -fbounds-check -fPIC/s/$/ -mcmodel=medium/' Source/make_opts
```

and resubmit the INTEGRATE step

```
cd -
iscmsconnect=1 bash -x gridpack_generation_all.sh <card_name> <card_dir> condor INTEGRATE
```



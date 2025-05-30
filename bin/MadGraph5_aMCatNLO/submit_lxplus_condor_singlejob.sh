#!/bin/bash

carddir=${1} # basename should be card name
nCpu=${2:-16} # 1 cpu per 2gb
jobflavour=${3:-"workday"}
outdir=${4:-"gridpacks"}

mkdir -p ${outdir}

name=$(basename $carddir)
scram_arch="slc7_amd64_gcc700"
cmssw_version=""

rm ${outdir}/${name}_script.sh
touch ${outdir}/${name}_script.sh
echo "source /cvmfs/cms.cern.ch/cmsset_default.sh" >> ${outdir}/${name}_script.sh
echo "cmssw-cc7 --bind /pool:/pool --bind /afs:/afs -- bash -c \"" >> ${outdir}/${name}_script.sh

echo "git clone https://github.com/cms-sw/genproductions" >> ${outdir}/${name}_script.sh

echo "cd genproductions/bin/MadGraph5_aMCatNLO/" >> ${outdir}/${name}_script.sh
echo "mv \${_CONDOR_SCRATCH_DIR}/$(basename ${carddir}) cards_to_run" >> ${outdir}/${name}_script.sh
echo "sed -i 's|/bin/generate_events|/bin/generate_events --nb_core=${nCpu}|g' gridpack_generation.sh" >> ${outdir}/${name}_script.sh
echo "./gridpack_generation.sh ${name} cards_to_run local ALL ${scram_arch} ${cmssw_version}" >> ${outdir}/${name}_script.sh
echo "cp *.xz $(dirname $(readlink -f ${outdir}/${name}_script.sh))/." >> ${outdir}/${name}_script.sh

echo "\"" >> ${outdir}/${name}_script.sh

condor_submit \
    executable=/bin/bash \
    RequestCpus=${nCpu} \
    output=${outdir}/${name}.out \
    error=${outdir}/${name}.err \
    log=${outdir}/${name}.log \
    stream_error=True \
    stream_output=True \
    transfer_input_files=${carddir},${outdir}/${name}_script.sh \
    transfer_output_files="\"\"" \
    -append "+JobFlavour=\"${jobflavour}\"" \
    -append "arguments=${name}_script.sh" \
    -append "queue 1" \
    /dev/null

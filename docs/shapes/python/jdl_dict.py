"""
jdl configuration file.

It includes a jdl dict with 
 - jdl_dict: all the optional variables that will be set in submit.jdl
 - executable: all the lines that will be written to run.sh
 - condor_config: all the options passed to condor_submit

Examples
--------
>>> 
>>> import os
>>> 
>>> # Get the current directory
>>> current_directory = os.getcwd()
>>> 
>>> mkshapesrdf_path = "/code/mkShapesRDF"
>>> 
>>> 
>>> project_path = current_directory
>>> 
>>> proxydir = "/builds/cms-analysis/smp/wpwmjj_polarizations/analysis_code"
>>> 
>>> singularity_container = os.getenv("SINGULARITY_CONTAINER")
>>> 
>>> jdl_dict = {
>>>     "transfer_input_files": f"{proxydir}/myproxy,$(Folder)/script.py, {mkshapesrdf_path}/include/headers.hh, {mkshapesrdf_path}/shapeAnalysis/runner.py, {project_path}/DR_lj.cc, {project_path}/bjets.cc,{project_path}/dnn_LLVsOther.cc,{project_path}/dnn_SigVsBkg.cc,{project_path}/dnn_TTVsOther.cc,{project_path}/m_lj.cc,{project_path}/proxyW.cc,{project_path}/generated_code_dnn_emu_LLVsOther.h,{project_path}/generated_code_dnn_emu_SigVsBkg.h,{project_path}/generated_code_dnn_emu_TTVsOther.h",
>>>     "transfer_output_files": "mkShapes__RDF_2017_v9_emu_DNN__ALL__$(Folder).root",
>>>     "+SingularityImage": f'"{singularity_container}/"',
>>>     "num_retries": "3",
>>>     "periodic_remove": "(JobStatus == 2) && (time() - EnteredCurrentStatus) > (0.25 * 3600) || (JobStatus == 1) && (time() - EnteredCurrentStatus) >(0.25 * 3600) || (JobStatus == 5) && (time() - EnteredCurrentStatus) > (0.1 * 3600)",
>>> }
>>> 
>>> 
>>> executable = [
>>>     "#!/bin/bash",
>>>     "source /code/start.sh",
>>>     "export X509_USER_PROXY=myproxy",
>>>     "export X509_CERT_DIR=/cvmfs/cms.cern.ch/grid/etc/grid-security/certificates",
>>>     "time python runner.py",
>>>     "mv output.root mkShapes__RDF_2017_v9_emu_DNN__ALL__${1}.root",
>>> ]
>>> 
>>> condor_config = ["-spool"]

"""

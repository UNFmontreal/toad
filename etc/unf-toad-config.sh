#Toad configuration file
#Copyright 2014, The Toad Project
#credits by Mathieu Desrosiers
# to be sourced by toad users, typically in .bash_profile or equivalent

#define TOAD directory
TOADDIR=$( cd "$( dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" )" && pwd )

#disable KMP_AFFINITY
export KMP_AFFINITY=none

#Freesurfer configuration
export FREESURFER_HOME=/usr/local/freesurfer
export FSFAST_HOME=$FREESURFER_HOME/fsfast
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/freesurfer/lib
export PERL5LIB=/usr/local/freesurfer/mni/lib/perl5/5.8.5:$PERL5LIB

# FSL Configuration
FSLDIR=/usr/local/fsl
export FSLOUTPUTTYPE=NIFTI_GZ
PATH=${FSLDIR}/bin:${PATH}:/usr/local/ants/build/bin
. ${FSLDIR}/etc/fslconf/fsl.sh
export FSLDIR PATH

export PATH=$PATH:$TOADDIR/bin:/usr/local/matlab-8.0/bin:/usr/local/mrtrix3/bin:/usr/local/mrtrix3/scripts:/usr/local/freesurfer/mni/bin:/usr/local/freesurfer/bin:/usr/local/freesurfer/tktools:/usr/local/c3d/bin:/usr/local/itksnap/bin:/usr/local/fibernavigator/bin

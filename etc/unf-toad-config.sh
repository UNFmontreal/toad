#!/usr/bin/env bash
#Toad configuration source file
#Copyright (C) 2014, TOAD
#License GPL v2
#Author Mathieu Desrosiers
#Credits by Mathieu Desrosiers, Arnaud Boré and Christophe Bedetti
#Maintainer Arnaud Boré and Christophe Bedetti
#Email toadunf.criugm@gmail.com

#to be sourced by toad users, typically in .bash_profile or equivalent

#define TOAD directory
TOADDIR=$( cd "$( dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" )" && pwd )

case "$HOSTNAME" in
    stark)
        export TOADSERVER=stark
        APPDIR=/usr/local
        export SGEQUEUE='toad.q'
    ;;
    magma)
        export TOADSERVER=magma
        APPDIR=/usr/local
        export PATH=/usr/local/python-toad/bin:$PATH
        export LD_LIBRARY_PATH=/usr/local/vtk/lib
        export SGEQUEUE='toad.q'
    ;;
    sati | physnum)
        export TOADSERVER=$HOSTNAME
        APPDIR=/usr/local
        export PATH=/usr/local/python-toad/bin:/usr/local/c3d/bin:/usr/local/itksnap/bin:/usr/local/fibernavigator/bin:$PATH
        export LD_LIBRARY_PATH=/usr/local/vtk/lib
        export SGEQUEUE='toad.q'
    ;;
    *)
    if [ -z "${BQMAMMOUTH}" ];
        then
            APPDIR=/usr/local
            export TOADSERVER=local
            echo "Warning, Toad is meant to dedicated server"
            echo "Please contact toadunf.criugm@gmail.com for further information"
            echo "unknown server $HOSTNAME, will guess environment!"
        else
            export TOADSERVER=mammouth
            APPDIR=/netmount/ip01_home/cbedetti/local/app_toad
            export LD_LIBRARY_PATH=$APPDIR/imagemagik-6.9/lib:$APPDIR/osmesa/lib:$APPDIR/lib:$APPDIR/vtk/lib:$APPDIR/python-2.7/lib:$LD_LIBRARY_PATH
            export PATH=$APPDIR/python-2.7/bin:$APPDIR/imagemagik-6.9/bin:$PATH
            export SGEQUEUE='qwork@mp2'
    fi
    ;;
esac


#disable KMP_AFFINITY
export KMP_AFFINITY=none

#force minc version 1 (netcdf) utilisation
export MINC_FORCE_V2=0

#disabled X11 utilisation into mayavi/tvtk package
export ETS_TOOLKIT='null'

#Freesurfer configuration
export FREESURFER_HOME=$APPDIR/freesurfer
export FSFAST_HOME=$FREESURFER_HOME/fsfast
export MINC_BIN_DIR=$FREESURFER_HOME/mni/bin
export MINC_LIB_DIR=$FREESURFER_HOME/mni/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$FREESURFER_HOME/lib
export PERL5LIB=$FREESURFER_HOME/mni/lib/perl5/5.8.5:$PERL5LIB

# FSL Configuration
FSLDIR=$APPDIR/fsl
export FSLOUTPUTTYPE=NIFTI_GZ
export FSLEDITOR=vi
PATH=${FSLDIR}/bin:${PATH}
. ${FSLDIR}/etc/fslconf/fsl.sh
export FSLDIR PATH

#export PATH=$TOADDIR/bin:$APPDIR/matlab/R2012b/bin:$APPDIR/mrtrix3/bin:$APPDIR/mrtrix3/scripts:$APPDIR/tract_querier:$PATH
export PATH=$TOADDIR/bin:$APPDIR/matlab/R2012b/bin:/home/bore/softs/mrtrix3/release/bin:/home/bore/softs/mrtrix3/scripts:$APPDIR/tract_querier:$PATH

# Fibernavigator
export PATH=:$APPDIR/fibernavigator/bin:$PATH

# Trackvis
export PATH=:$APPDIR/trackvis/v0.6.0.1_x86_64:$PATH

export PATH=$FREESURFER_HOME/mni/bin:$FREESURFER_HOME/bin:$FREESURFER_HOME/tktools:$PATH



# SCILPY Configuration
export PYTHONPATH=/home/bore/softs/scilpy:$PYTHONPATH
export PATH=/home/bore/softs/scilpy/scripts:$PATH

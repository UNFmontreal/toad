import os

class Tractography(object):


    def tckgen(self, source, target, mask = None, act = None , seed_gmwmi = None, bFile = None, algorithm = "iFOD2"):
        """ perform streamlines tractography.

             the image containing the source data. The type of data
             depends on the algorithm used:
             - FACT: the directions file (each triplet of volumes is
             the X,Y,Z direction of a fibre population).
             - iFOD1/2 & SD_Stream: the SH image resulting from CSD.
             - Nulldist & SeedTest: any image (will not be used).
             - TensorDet / TensorProb: the DWI image.

        Args:
            source: the image containing the source data.
            target: the output file containing the tracks generated.
            bFile: specify the diffusion-weighted gradient scheme used in the acquisition.
            mask: specify a masking region of interest, as a binary mask image.
            act: use the Anatomically-Constrained Tractography framework during tracking
            seed_gmwmi: seed from the grey matter - white matter interface (only valid if using ACT framework)
            algorithm: the tractography algorithm to use. default: iFOD2

        Returns:
            The resulting streamlines tractography filename generated

        """
        self.info("Starting tckgen creation from mrtrix on {}".format(source))
        tmp = os.path.join(self.workingDir, "tmp_{}.tck".format(algorithm))

        cmd = "tckgen {} {}  -mask {} -act {} -seed_gmwmi {} -number {} -algorithm {} -nthreads {} -quiet"\
            .format(source, tmp, mask,  act, seed_gmwmi, self.get( 'number_tracks'), algorithm, self.getNTreadsMrtrix())

        if bFile is not None:
            cmd += " -grad {}".format(bFile)

        self.launchCommand(cmd)
        self.info("renaming {} to {}".format(tmp, target))
        os.rename(tmp, target)

        return target


    def tck2connectome(self, source, nodes, target):
        """ generate a connectome matrix from a streamlines file and a node parcellation image

        Args:
            source: the input track file
            nodes: the input parcellation image
            target: the output .csv file containing edge weights

        Returns:
            The resulting .cvs file name

        """
        self.info("Starting tck2connectome from mrtrix on {}".format(source))
        tmp = os.path.join(self.workingDir, "tmp.csv")
        cmd = "tck2connectome {} {} {} -quiet -nthreads {}".format(source, nodes, tmp, self.getNTreadsMrtrix() )

        self.launchCommand(cmd)
        self.info("renaming {} to {}".format(tmp, target))
        os.rename(tmp, target)

        return target


    def tcksift(self, source, dwi2fod):
        """ filter a whole-brain fibre-tracking data set such that the streamline densities match the FOD lobe integral.

        Args:
            source: the input track file.
            dwi2fod: input image containing the spherical harmonics of the fibre orientation distributions

        Returns:
            The resulting output filtered tracks file

        """
        tmp = os.path.join(self.workingDir,"tmp_tcksift.tck")
        target = self.getTarget(source, 'tcksift','.tck')
        self.info("Starting tcksift creation from mrtrix on {}".format(source))

        cmd = "tcksift {} {} {} -nthreads {} -quiet".format(source, dwi2fod, tmp, self.getNTreadsMrtrix())
        self.launchCommand(cmd)

        self.info("renaming {} to {}".format(tmp, target))
        os.rename(tmp, target)
        return target





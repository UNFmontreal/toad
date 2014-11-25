if isempty(which('spm'))
    throw(MException('SPMCheck:NotFound', 'SPM not in matlab path'));
end
[name, version] = spm('ver');
fprintf('SPM version: %s Release: %s\n',name, version);
fprintf('SPM path: %s\n', which('spm'));
spm('Defaults','fMRI');
if strcmp(name, 'SPM8') || strcmp(name, 'SPM12b')
    spm_jobman('initcfg');
    spm_get_defaults('CmdLine', 1);
end

jobs{1}.spm.spatial.preproc.output.GM(1) = $gm1;
jobs{1}.spm.spatial.preproc.output.GM(2) = $gm2;
jobs{1}.spm.spatial.preproc.output.GM(3) = $gm3;
jobs{1}.spm.spatial.preproc.output.CSF(1) = $csf1;
jobs{1}.spm.spatial.preproc.output.CSF(2) = $csf2;
jobs{1}.spm.spatial.preproc.output.CSF(3) = $csf3;
jobs{1}.spm.spatial.preproc.output.WM(1) = $wm1;
jobs{1}.spm.spatial.preproc.output.WM(2) = $wm2;
jobs{1}.spm.spatial.preproc.output.WM(3) = $wm3;
jobs{1}.spm.spatial.preproc.data = {...
    '$source,1';...
};
spm_jobman('run', jobs);
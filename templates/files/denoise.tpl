clc;
clear all;
warning off;
rician=1;  % 1 for bias correction and 0 to disable it.
nbthreads=$nbthreads; % number of threads submit
V=spm_vol('$source');
ima=spm_read_vols(V);
[fima] = DWIDenoisingLPCA(ima, rician, nbthreads);
% save result
ss=size(V);
for ii=1:ss(1)
    V(ii).fname='$target';
    spm_write_vol(V(ii), fima(:,:,:,ii));
end






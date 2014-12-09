clc;
clear all;
warning off;
beta =$beta;
rician=$rician;  % 1 for rician noise model and 0 for gaussian noise model.
nbthreads=$nbthreads; % number of threads submit
verbose=0;
V=spm_vol('$source');
ima=spm_read_vols(V);
[fima] = DWIDenoisingLPCA(ima, beta, rician, nbthreads, verbose);
% save result
ss=size(V);
for ii=1:ss(1)
    V(ii).fname='$target';
    spm_write_vol(V(ii), fima(:,:,:,ii));
end






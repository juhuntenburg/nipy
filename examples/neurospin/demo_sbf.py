"""
This scipt generates a noisy activation image image
and applies the bayesian structural analysis on it

Author : Bertrand Thirion, 2009
"""
#autoindent

import numpy as np
import scipy.stats as st
import matplotlib.pylab as mp
import fff2.graph.field as ff
import fff2.utils.simul_2d_multisubject_fmri_dataset as simul
import fff2.spatial_models.structural_bfls as sbf

def make_bsa_2d(betas, theta=3., dmax=5., ths=0, thq=0.5, smin=0, 
                        nbeta=[0]):
    """ Function for performing bayesian structural analysis on a set of images.
    """
    ref_dim = np.shape(betas[0])
    nbsubj = betas.shape[0]
    xyz = np.array(np.where(betas[:1]))
    nbvox = np.size(xyz, 1)
    
    # create the field strcture that encodes image topology
    Fbeta = ff.Field(nbvox)
    Fbeta.from_3d_grid(xyz.astype(np.int).T, 18)

    # Get  coordinates in mm
    xyz = np.transpose(xyz)
    tal = xyz.astype(np.float)

    # get the functional information
    lbeta = np.array([np.ravel(betas[k]) for k in range(nbsubj)]).T

    header = None
    group_map, AF, BF, labels = sbf.Compute_Amers (Fbeta,lbeta,xyz,header, tal,dmax = 10., thr=3.0, ths = nbsubj/2,pval=0.2)
    
    labels[labels==-1] = np.size(AF)+2
  
    group_map.shape = ref_dim
    mp.figure()
    mp.imshow(group_map, interpolation='nearest', vmin=-1, vmax=labels.max())
    mp.title('Group-level label map')
    mp.colorbar()

    sub = np.concatenate([s*np.ones(BF[s].k) for s in range(nbsubj)])
    mp.figure()
    if nbsubj==10:
        for s in range(nbsubj):
            mp.subplot(2, 5, s+1)
            lw = -np.ones(ref_dim)
            nls = BF[s].get_roi_feature('label')
            nls[nls==-1] = np.size(AF)+2
            for k in range(BF[s].k):
                xyzk = BF[s].discrete[k].T 
                lw[xyzk[1],xyzk[2]] =  nls[k]

            mp.imshow(lw, interpolation='nearest', vmin=-1, vmax=labels.max())
            mp.axis('off')

    mp.figure()
    if nbsubj==10:
        for s in range(nbsubj):
            mp.subplot(2,5,s+1)
            mp.imshow(betas[s],interpolation='nearest',vmin=betas.min(),vmax=betas.max())
            mp.axis('off')

    return AF, BF


################################################################################
# Main script
################################################################################

# generate the data
nbsubj=10

dimx=60
dimy=60
pos = 2*np.array([[ 6,  7],
                  [10, 10],
                  [15, 10]])
ampli = np.array([5, 7, 6])
sjitter = 1.0
dataset = simul.make_surrogate_array(nbsubj=nbsubj, dimx=dimx, dimy=dimy, 
                                     pos=pos, ampli=ampli, width=5.0)
betas = np.reshape(dataset, (nbsubj, dimx, dimy))

# set various parameters
theta = float(st.t.isf(0.01, 100))
dmax = 5./1.5
ths = 0#nbsubj/2-1
thq = 0.9
verbose = 1
smin = 5

# run the algo
AF, BF = make_bsa_2d(betas, theta, dmax, ths, thq, smin)
mp.show()


from readers import PARS
import time
from mrec import load_recommender
import numpy as np
import mrec

def make_mrec_outfile(infile,d,num_iters,reg):
    suffix="_mrec_d%s_iter%s_reg%0.4f.npz"%(d,num_iters,reg)
    outfile = infile.replace('.csv',suffix)
    return outfile

def multi_thresh(data,model,thresh_list=None):
    import pickle
    if thresh_list==None: thresh_list=np.linspace(-0.2,1.0,40)
    vals=[]
    print " thresh  precision  recall  fscore"
    print "-----------------------------------------"
    for thresh in thresh_list:
        val=validate_matrices(data,model,thresh=thresh)
        val['thresh']=thresh

        vals.append(val)
        line="%0.4f  %0.4f  %0.4f  %0.4f)"%(thresh, val['precision'],val['recall'],val['fscore'])
        print line
    pickle.dump(vals,open('data.pickle','wb'))

    return vals

def threshing(M_sparse,U,V,thresh=0.5):
    ''' 
    Calculate the sufficient statistics between a 
    sparse matrix and a UV decomposed one  
    We want: 
    d= sum_of M_sparse
    c= sum_of ((M_sparse * U*V^T) > thresh)
    s= sum_of (U*V^T > thresh)
    These can be used to calculate precision, recall, AUROC etc
    for matrix factorization models without expanding into full matrices
    assumes M_sparse is a list of (row,col) tupes where the value is 1 , else 0
    U and V are the U-V decomposition via a matrix factorization.
    This should be both memory efficient and fast, thus, allowing for huge data sets.
    TODO:this needs work
    '''
       
    num_U=U.shape[0]
    num_V=V.shape[0]
    num_tot=float(num_U*num_V)
    num_d=U.shape[1]
    assert(V.shape[1] == num_d)

    mean_data=len(M_sparse)/num_tot
    print 'mean data: %s'%mean_data

    sum_cross=0.0
    for row, col in M_sparse:
        u=U[row,:]
        v=V[col,:]
        sum_cross+= (np.dot(u,v))> thresh
        
    x=[d[0] for d in M_sparse]
    y=[d[1] for d in M_sparse]
    U_filt=U[x,:]
    V_filt=V[y,:]
    

    mean_cross=sum_cross/num_tot
    print 'mean cross: %s'%mean_cross

    sum_model=0.0
    for i in xrange(num_U):
        sum_model+=(np.dot(V,U[i,:]) > thresh).sum()
    sum_cross2=0.0
    for i in x:
        sum_cross2+=(np.dot(V_filt,U[i,:]) > thresh).sum()
    mean_cross=sum_cross2/num_tot
    print 'mean cross2: %s'%mean_cross2
        

    mean_model=sum_model/num_tot
    print 'mean model: %s'%mean_model
    #return means not sums
    return (mean_data,mean_model,mean_cross)

def validate_matrices(data,model,thresh=0.5,show=False):
    rms=np.sqrt(((data-model)**2).mean())
    mean_data=data.mean()
    mean_model=model.mean()
    mean_ratio=mean_model/float(mean_data)
    sim=(model>thresh)*1
    mean_sim=sim.mean()
    mean_cross=(data*sim).mean()
    #print 'memory ok?'
    
    #true_pos, true_neg, false_pos,false_neg RATES
    #ROC is plot of x=fallout, y=recall
    
    #be memory efficient
    #TP=( data*sim ).mean()
    #TN=( (1-data)*(1-sim) ).mean()
    #FP=( (1-data)*sim ).mean()
    #FN=( data*(1-sim) ).mean()

    TP=mean_cross                                                                                
    TN=1-mean_data-mean_sim+mean_cross                                                          
    FP=mean_sim-mean_cross                                                                                 
    FN=mean_data-mean_cross     

    ep=1e-11
    precision=TP/(TP+FP+ep)
    recall=TP/(TP+FN+ep)
    fallout=FP/(FP+TN+ep)
    fscore=2*precision*recall/(precision+recall)

    valid={'rms':rms,'mean_data':mean_data,'mean_model':mean_model,'mean_ratio':mean_ratio,
           'TP':TP,'FP':FP,'TN':TN,'FN':FN,'mean_cross':mean_cross,
           'precision':precision,'recall':recall,'fallout':fallout,'fscore':fscore}
    if show:
        for k,v in valid.iteritems(): print k,":",v
    return valid

def read_mrec(mrec_file='reduced.v1_numbers_mrec_d5_iter9_reg0.0150.npz'):
    file_name=PARS['data_dir']+mrec_file
    data_file_name=file_name.split('_mrec_')[0]+'.csv'
    model=mrec.load_recommender(file_name)
    U=model.U
    V=model.V
    model_matrix=np.dot(U,V.transpose())
    shape=model_matrix.shape
    shape=(U.shape[0],V.shape[0])
    data_matrix=np.ndarray(shape,dtype=int)
    line_num=0
    #data_list=[]
    for line in open(data_file_name,'r'):
        line_num+=1
        if line_num % 1000000 ==0 : print line_num
        dat=line.strip().split(',')
        row=int(dat[0])-1
        col=int(dat[1])-1
        val=int(float(dat[2]))
        assert(val == 1)
        #data_list.append((row,col))
        data_matrix[row,col]=val
    return (data_matrix,U,V)

def test_mrec(d=5,num_iters=3,reg=0.015):
    #d is dimension of subspace, i.e. groups
    import sys
    from mrec import load_sparse_matrix, save_recommender
    from mrec.sparse import fast_sparse_matrix
    from mrec.mf.wrmf import WRMFRecommender

    alpha=1.0
    start=time.time()

    file_format = "csv"
    #file shoule be csv, with: row,col,data
    #data may just be ones
    filepath = PARS['data_dir']+"reduced.v1_numbers.csv"
    #filepath = PARS['data_dir']+"test_10_mill.csv" 
    outfile = make_mrec_outfile(filepath,d,num_iters,reg)
    print outfile
    print 'reading file: %s'%filepath
    # load training set as scipy sparse matrix
    print "loading file"
    train = load_sparse_matrix(file_format,filepath)
    print "loaded file"
    print (time.time()-start),"seconds"
    print "size:",train.shape

    print "creating recommender"
    model = WRMFRecommender(d=d,num_iters=num_iters,alpha=alpha,lbda=reg)
    print "training on data"
    print time.time()-start
    model.fit(train)
    print "done training"
    print time.time()-start
    print "saving model"
    save_recommender(model,outfile)
    print "wrote model to: %s"%outfile
    print "done"
    run_time=(time.time()-start)/60.0
    print "runtime: %0.3f minutes"%run_time




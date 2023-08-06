    extern "C"{
    
        __device__ myFex myfex;
        __device__ myJex myjex;
        
        __global__ void init_common(){
            int tid = blockDim.x * blockIdx.x + threadIdx.x;
            cuLsodaCommonBlockInit( &(common[tid]) );
        }
        
        __global__ void cuLsoda(int *neq, double *g_y, double *t, double *tout, int *itol, 
        			double *rtol, double *atol, int *itask, int *istate, int *iopt, 
        			double *g_rwork, int *lrw, int *iwork, int *liw, int *jt, int *isize, int *rsize) {

            int tid = blockIdx.x;

            dlsoda_(myfex, neq, g_y+tid*neq[0], t+tid, tout+tid, itol, rtol, atol, itask,
                istate+tid, iopt, g_rwork+tid*rsize[0], lrw, iwork+tid*isize[0], liw, myjex, jt, &(common[tid]) );

        }
    }
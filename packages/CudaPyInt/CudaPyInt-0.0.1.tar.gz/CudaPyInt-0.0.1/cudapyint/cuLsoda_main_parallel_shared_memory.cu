    extern "C"{
    
        __device__ myFex myfex;
        __device__ myJex myjex;
        
        __global__ void init_common(){
            int tid = blockDim.x * blockIdx.x + threadIdx.x;
            cuLsodaCommonBlockInit( &(common[tid]) );
        }
        
        __global__ void cuLsoda(int *g_neq, double *g_y, double *g_t,
        		double *g_tout, int *g_itol, double *g_rtol, double *g_atol, int *g_itask,
        		int *g_istate, int *g_iopt, double *g_rwork, int *g_lrw, int *g_iwork,
        		int *g_liw, int *g_jt, int *isize, int *rsize) {

        	__shared__ int neq;
        	__shared__ int itol;
        	__shared__ double rtol;
        	__shared__ int itask;
        	__shared__ int iopt;
        	__shared__ int lrw;
        	__shared__ int liw;
        	__shared__ int jt;
        	__shared__ double t;
        	__shared__ double tout;
        	__shared__ int istate;

        	__shared__ double y[NEQ];
        	__shared__ double atol[NEQ];
        	__shared__ int iwork[20+NEQ];
            if(threadIdx.x==0){
        		neq = g_neq[0];
        		itol = g_itol[0];
        		rtol = g_rtol[0];
        		itask = g_itask[0];
        		iopt = g_iopt[0];
        		lrw = g_lrw[0];
        		liw = g_liw[0];
        		jt = g_jt[0];

        		t = g_t[blockIdx.x];
        		tout = g_tout[blockIdx.x];
        		istate = g_istate[blockIdx.x];

        		memcpy(y, g_y+blockIdx.x*neq, sizeof(double)*neq);
        		memcpy(atol, g_atol, sizeof(double)*neq);
        		memcpy(iwork, g_iwork+blockIdx.x*isize[0], sizeof(int)*isize[0]);
            }
        	__syncthreads();

            dlsoda_(myfex, &neq, y, &t, &tout, &itol, &rtol, atol, &itask,
                &istate, &iopt, g_rwork+blockIdx.x*rsize[0], &lrw, iwork, &liw, myjex, &jt, &(common[blockIdx.x]) );

            if(threadIdx.x==0){
            	g_istate[blockIdx.x] = istate;
            	memcpy(g_y+blockIdx.x*neq, y, sizeof(double)*neq);
            	memcpy(g_iwork+blockIdx.x*isize[0], iwork, sizeof(int)*isize[0]);
            }
        //    __syncthreads();
        }
    }
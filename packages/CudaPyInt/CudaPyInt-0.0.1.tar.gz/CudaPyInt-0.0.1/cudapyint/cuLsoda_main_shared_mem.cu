    extern "C"{
    
        __device__ myFex myfex;
        __device__ myJex myjex;
        
        __global__ void init_common(){
            int tid = blockDim.x * blockIdx.x + threadIdx.x;
            cuLsodaCommonBlockInit( &(common[tid]) );
        }
        
        __global__ void cuLsoda(const int *g_neq, double *g_y, double *g_t,
        		double *g_tout, const int *g_itol, const double *g_rtol, double *atol, const int *g_itask,
        		int *g_istate, const int *g_iopt, double *rwork, const int *g_lrw, int *iwork,
        		const int *g_liw, const int *g_jt, int *isize, int *rsize) {

        	int tid = blockDim.x * blockIdx.x + threadIdx.x;
        	__shared__ int neq;
        	neq = g_neq[0];
        	__shared__ int itol;
        	itol = g_itol[0];
        	__shared__ double rtol;
        	rtol = g_rtol[0];
        	__shared__ int itask;
        	itask = g_itask[0];
        	__shared__ int iopt;
        	iopt = g_iopt[0];
        	__shared__ int lrw;
        	lrw = g_lrw[0];
        	__shared__ int liw;
        	liw = g_liw[0];
        	__shared__ int jt;
        	jt = g_jt[0];

        	__shared__ double t[BLOCK_SIZE];
        	t[threadIdx.x] = g_t[tid];
        	__shared__ double tout[BLOCK_SIZE];
        	tout[threadIdx.x] = g_tout[tid];
        	__shared__ int istate[BLOCK_SIZE];
        	istate[threadIdx.x] = g_istate[tid];

        	__shared__ double y[BLOCK_SIZE*NEQ];
        	memcpy(y+threadIdx.x*neq, g_y+tid*neq, sizeof(double)*neq);


        	//printf("*tid:%i t:%4.2f t:%4.2f \t y=[%G %G %G %G %G %G %G]\n", tid, t[tid], tout[tid], y[threadIdx.x*neq+0], y[threadIdx.x*neq+1], y[threadIdx.x*neq+2], y[threadIdx.x*neq+3], y[threadIdx.x*neq+4], y[threadIdx.x*neq+5], y[threadIdx.x*neq+6]);
        	//printf("*tid:%i t:%4.2f %4.2f t:%4.2f %4.2f \n", tid, t[tid], g_t[tid], tout[tid], g_tout[tid]);

        	dlsoda_(myfex, &neq, &y[threadIdx.x*neq], &t[threadIdx.x], &tout[threadIdx.x], &itol, &rtol,
        			atol, &itask, &istate[threadIdx.x], &iopt, rwork + tid * rsize[0], &lrw,
        			iwork + tid * isize[0], &liw, myjex, &jt, &(common[tid]));

        	g_t[tid] = t[threadIdx.x];
        	g_tout[tid] = tout[threadIdx.x];
        	g_istate[tid] = istate[threadIdx.x];
        	memcpy(g_y+tid*neq, y+threadIdx.x*neq, sizeof(double)*neq);

        }
    }
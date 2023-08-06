#include <stdio.h>
#include <stdlib.h>

__device__ double computeHa(double a){
	double ha;
	if (a < ha_a[0])
		ha = ha_y[0];
	else if (a > ha_a[ha_a_len - 1])
		ha = ha_y[ha_y_len - 1];
	else {
		int l, r, m;
		for (l = 0, r = ha_a_len - 1, m = (l + r) / 2; 1 < r - l; m = (l + r) / 2)
			if (a < ha_a[m])
				r = m;
			else
				l = m;
        ha = (a - ha_a[l]) / (ha_a[r] - ha_a[l]) * ha_y[l] + (ha_a[r] - a) / (ha_a[r] - ha_a[l]) * ha_y[r];
	}
	return ha;
}

__device__ double computeXe(double a){
	double xe;
	if (a < rec_a[0])
		xe = rec_xe[0];
	else if (a > rec_a[rec_a_len - 1])
		xe = rec_xe[rec_xe_len - 1];
	else {
		int l, r, m;
		for (l = 0, r = rec_a_len - 1, m = (l + r) / 2; 1 < r - l; m = (l + r) / 2)
			if (a < rec_a[m])
				r = m;
			else
				l = m;
        xe = (a - rec_a[l]) / (rec_a[r] - rec_a[l]) * rec_xe[l] + (rec_a[r] - a) / (rec_a[r] - rec_a[l]) * rec_xe[r];
	}
	return xe;
}

__device__ double computeEta(double a){
	double eta;
	if (a < ha_a[0])
		eta = eta_a[0];
	else if (a > ha_a[ha_a_len - 1])
		eta = eta_a[eta_a_len - 1];
	else {
		int l, r, m;
		for (l = 0, r = ha_a_len - 1, m = (l + r) / 2; 1 < r - l; m = (l + r) / 2)
			if (a < ha_a[m])
				r = m;
			else
				l = m;
		eta = (a - ha_a[l]) / (ha_a[r] - ha_a[l]) * eta_a[l] + (ha_a[r] - a) / (ha_a[r] - ha_a[l]) * eta_a[r];
	}
	return eta;
}



struct myFex{
    __device__ void operator()(int *neq, double *ts, double *y, double *dy/*, void *otherData*/)
    {
        int tid = blockDim.x * blockIdx.x + threadIdx.x;
        
        int len = neq[0];
        
        double t = ts[0];
        
        double a = exp(t);
        float k = tex2D(args_tex,1, tid);
        
        double ha = computeHa(a);

        // (see Dodelson eq. 3.45, p73); [h Mpc^-1; caution: a factor of h may be missing; also this neglect He and so needs to be revised
    	double xe = computeXe(a);
    	
        double tdot = -0.0692 / pow(a, 2) * xe * omega_b * h / rh;

		if (len == 7) {
			double dphi = -(1. + pow(k, 2) / (3. * pow(a, 2) * pow(ha, 2))) * y[0]
						+ 0.5 / pow(ha * rh, 2) * (omega_dm * pow(a, -3) * y[1] + omega_b * pow(a, -3) * y[3] + 4. * omega_r * pow(a, -4) * y[5]);
			double r_bph = 3. / 4. * omega_b / omega_gam * a;
			
			dy[0] = dphi; // phi, 0
			dy[1] = -k / (a * ha) * y[2] - 3. * dphi; // delta, 1
			dy[2] = -y[2] - k / (a * ha) * y[0]; // u = i*v, 2
			dy[3] = -k / (a * ha) * y[4] - 3. * dphi; // delta_b, 3
			dy[4] = -y[4] - k / (a * ha) * y[0] + tdot / (r_bph * a * ha) * (y[4] - 3. * y[6]); // u_b, 4
			dy[5] = -k / (a * ha) * y[6] - dphi; // theta0, 5
			dy[6] = k / (3. * a * ha) * (y[5] - y[0]) + tdot / (a * ha) * (y[6] - y[4] / 3.); // theta1, 6
	

		} else {

			int lmax = (len - 5) / 2;
			double eta = computeEta(a);

			int l;

			double psi = -y[0] - 12. * pow(k * a * rh, 2) * omega_r * y[7];
			double dphi = psi - 1./3. * pow(k / (a * ha), 2) * y[0]
						+ 0.5 / pow(ha * rh, 2) * (omega_dm * pow(a, -3) * y[1] + omega_b * pow(a, -3) * y[3] + 4. * omega_r * pow(a, -4) * y[5]);
			double r_bph = 3. / 4. * omega_b / omega_gam * a;
			double Pi = y[7] + y[5 + lmax] + y[5 + lmax + 2];

			dy[0] = dphi; // phi, 0
			dy[1] = -k / (a * ha) * y[2] - 3. * dphi; // delta, 1
			dy[2] = -y[2] + k / (a * ha) * psi; // u = i*v, 2
			dy[3] = -k / (a * ha) * y[4] - 3. * dphi; // delta_b, 3
			dy[4] = -y[4] + k / (a * ha) * psi + tdot / (r_bph * a * ha) * (y[4] - 3. * y[6]); // u_b, 4

			dy[5] = -k / (a * ha) * y[6] - dphi; // theta_0, 5
			dy[6] = 1./3. * k / (a * ha) * (y[5] - y[7] + psi) + tdot / (a * ha) * (y[6] - y[4] / 3.); // theta_1, 6

			dy[7] = 1./5. * k / (a * ha) * (2. * y[6] - 3. * y[8]) + tdot / (a * ha) * (y[7] - Pi / 10.); // theta_2, 7

			l = 0;
			dy[5 + lmax] = k / (a * ha) * 1 / (2 * l + 1) * (-(l + 1)* y[5 + lmax + 1])
					+ tdot / (a * ha) * (y[5 + lmax] - Pi / 2. * 1. ); // theta_p0, 5 + l_max + 0

			l = 1;
			dy[5 + lmax + l] = k / (a * ha) * 1 / (2 * l + 1) * (l * y[5 + lmax + l - 1] - (l + 1) * y[5 + lmax + l + 1])
				+ tdot / (a * ha) * (y[5 + lmax + l]); // theta_p1, 5 + l_max + 1

			l = 2;
			dy[5 + lmax + l] = k / (a * ha) * 1 / (2 * l + 1) * (l * y[5 + lmax + l - 1] - (l + 1) * y[5 + lmax + l + 1])
					+ tdot / (a * ha) * (y[5 + lmax + l] - Pi / 2. * 1. / 5. ); // theta_p2, 5 + l_max + 2

			for (l = 3; l < lmax-1; l++) {
				dy[5 + l] = k / (a * ha) * 1 / (2 * l + 1) * (l * y[5 + l - 1] - (l + 1) * y[5 + l + 1])
					+ tdot / (a * ha) * y[5 + l]; // theta_l, 5 + l

				dy[5 + lmax + l] = k / (a * ha) * 1 / (2 * l + 1) * (l * y[5 + lmax + l - 1] - (l + 1) * y[5 + lmax + l + 1])
					+ tdot / (a * ha) * (y[5 + lmax + l]); // theta_pl, 5 + l_max + l
			}

			l = lmax - 1;

			dy[5 + l] = 1 / (a * ha) * (k * y[5 + l - 1] - ((l * 1) / eta - tdot) * y[5 + l]); // theta_l_max, 5 + lmax

			dy[5 + lmax + l] = 1 / (a * ha) * (k * y[5 + lmax + l - 1] - ((l * 1) / eta - tdot) * y[5 + lmax + l]); // theta_pl_max, 5 + 2*l_max

		}
    }
};

struct myJex{
    __device__ void operator()(int *neq, double *ts, double *y, int ml, int mu, double *dy, int nrowpd/*, void *otherData*/){
    	int tid = blockDim.x * blockIdx.x + threadIdx.x;
    	
        int len = neq[0];
        int lmax = (len - 5) / 2;
        
        double t = ts[0];
        
        double a = exp(t);
        float k = tex2D(args_tex,1, tid);
        
    	double ha = computeHa(a);
        // (see Dodelson eq. 3.45, p73); [h Mpc^-1; caution: a factor of h may be missing; also this neglect He and so needs to be revised
    	double xe = computeXe(a);
		
		double tdot = -0.0692 / pow(a, 2) * xe * omega_b * h / rh;
        double r_bph = 3. / 4. * omega_b / omega_gam * a;
        
        double harh2 = pow(ha * rh, 2);
        double kaha = k / (a * ha);
        double tdotaha = tdot / (a * ha);
        double tdotaha3 = tdotaha / 3;
        double tdotaha10 = tdotaha / 10;
        double a2 = pow(a, 2);
        double a3 = pow(a, 3);
        double am3 = pow(a, -3);
        double am4 = pow(a, -4);
        double ha2 = pow(ha, 2);
        double k2 = pow(k, 2);
        
        double a2k2 = a2 * k2;
        
        double rhi2 = pow(1 / rh, 2);
        
        double harh2_omega_dm_a3 = harh2 * omega_dm * (2 * am3);
        double harh2_omega_b_a3 = harh2 * omega_b * (2 * am3);
        double harh2_omega_r_a4 = harh2 * omega_r * am4;
        

        memset(dy, 0, len*len*sizeof(double));

    	#define I(j, i) (i * len + j)

        int i = 0;
    	dy[I(i, 0)] = -( k2 / (3. * a2 * ha2)) - 1.;
    	dy[I(i, 1)] = 1. / harh2_omega_dm_a3;
    	//dy[I(i, 2)] = 0;
    	dy[I(i, 3)] = 1. / harh2_omega_b_a3;
    	//dy[I(i, 4)] = 0;
    	dy[I(i, 5)] = 2. / harh2_omega_r_a4;
    	//dy[I(i, 6)] = 0;

    	i = 1;
    	dy[I(i, 0)] = ( k2 / (a2 * ha2)) + 3.;
    	dy[I(i, 1)] = -3. / harh2_omega_dm_a3;
    	dy[I(i, 2)] = -kaha;
    	dy[I(i, 3)] = -3. / harh2_omega_b_a3;
    	//dy[I(i, 4)] = 0;
    	dy[I(i, 5)] = -6. / harh2_omega_r_a4;
    	//dy[I(i, 6)] = 0;

    	i = 2;
    	dy[I(i, 0)] = -kaha;
    	//dy[I(i, 1)] = 0;
    	dy[I(i, 2)] = -1;
    	//dy[I(i, 3)] = 0;
    	//dy[I(i, 4)] = 0;
    	//dy[I(i, 5)] = 0;
    	//dy[I(i, 6)] = 0;

    	i = 3;
    	dy[I(i, 0)] = ( k2 / (a2 * ha2)) + 3;
    	dy[I(i, 1)] = -3. / harh2_omega_dm_a3;
    	//dy[I(i, 2)] = 0;
    	dy[I(i, 3)] = -3. / harh2_omega_b_a3;
    	dy[I(i, 4)] = -kaha;
    	dy[I(i, 5)] = -6. / harh2_omega_r_a4;
    	//dy[I(i, 6)] = 0;

    	i = 4;
    	dy[I(i, 0)] = -kaha;
    	//dy[I(i, 1)] = 0;
    	//dy[I(i, 2)] = 0;
    	//dy[I(i, 3)] = 0;
    	dy[I(i, 4)] = -1. + tdot / (r_bph * a * ha);
    	//dy[I(i, 5)] = 0;
    	dy[I(i, 6)] = -3. * tdot / (r_bph * a * ha);

    	i = 5; //dtheta 0
    	dy[I(i, 0)] = ( k2 / (3. * a2 * ha2)) + 1.;
    	dy[I(i, 1)] = -1. / harh2_omega_dm_a3;
    	//dy[I(i, 2)] = 0;
    	dy[I(i, 3)] = -1. / harh2_omega_b_a3;
    	//dy[I(i, 4)] = 0;
    	dy[I(i, 5)] = -2. / harh2_omega_r_a4;
    	dy[I(i, 6)] = -kaha;

    	i = 6; //dtheta 1
    	dy[I(i, 0)] = -k/ (3. * a * ha);
    	//dy[I(i, 1)] = 0;
    	//dy[I(i, 2)] = 0;
    	//dy[I(i, 3)] = 0;
    	dy[I(i, 4)] = -tdotaha3;
    	dy[I(i, 5)] = k / (3. * a * ha);
    	dy[I(i, 6)] = tdotaha;

    	if(len>7){

    		//theta2
    		dy[I(0, 7)] = -12 * rhi2 * omega_r / (a2k2);
    		dy[I(1, 7)] = 36 * rhi2 * omega_r / (a2k2);
    		dy[I(2, 7)] = -12 / harh2 * omega_r / (a3 * ha * k);
    		dy[I(3, 7)] = 36 * rhi2 * omega_r / (a2k2);
    		dy[I(4, 7)] = -12 / harh2 * omega_r / (a3 * ha * k);
    		dy[I(5, 7)] = 12 * rhi2 * omega_r / (a2k2);
    		dy[I(6, 7)] = -(a2k2 + 12 * rhi2 * omega_r) / (3 * a3 * ha * k);

    		if(lmax>3){
    			i = 7; //dtheta 2
//    			dy[I(i, 0)] = 0;
//    			dy[I(7, 1)] = 0;
//    			dy[I(7, 2)] = 0;
//    			dy[I(7, 3)] = 0;
//    			dy[I(7, 4)] = 0;
//    			dy[I(7, 5)] = 0;
    			dy[I(7, 6)] = 2 * k / (5 * a * ha);
    			dy[I(7, 7)] = 9 * tdotaha10;
    			dy[I(7, 8)] = -3 * k / (5 * a * ha);
    			dy[I(7, (5 + lmax + 0))] = -tdotaha10;
    			dy[I(7, (5 + lmax + 2))] = -tdotaha10;
    		}

    		int l;
    		l=0; //dtheta p 0
    		dy[I((5 + lmax + l), 7)] = -tdot / (2 * a * ha);
    		dy[I((5 + lmax + l), (5 + lmax + 0))] = tdot / (2 * a * ha);
    		//dy[I((5 + lmax + l), (5 + lmax + 1))] = (k + k * l) / (a * ha * (2 * l + 1));
    		dy[I((5 + lmax + l), (5 + lmax + 1))] = kaha * l / (1 + 2 * l);
    		dy[I((5 + lmax + l), (5 + lmax + 2))] = -tdot / (2 * a * ha);

    		l=1; //dtheta p 1
    		//dy[I((5 + lmax + l), (5 + lmax + 0))] = (k * l) / (a * ha * (2 * l + 1));
    		dy[I((5 + lmax + l), (5 + lmax + 0))] = kaha * l / (1 + 2 * l);
    		dy[I((5 + lmax + l), (5 + lmax + 1))] = tdotaha;
    		//dy[I((5 + lmax + l), (5 + lmax + 2))] = -(k + k * l) / (a * ha * (2 * l + 1));
    		dy[I((5 + lmax + l), (5 + lmax + 2))] = -kaha * (1 + l) / (1 + 2 * l);

    		if(lmax>3){
    			l=2; //dtheta p 2
    			dy[I((5 + lmax + l), 7)] = -tdotaha10;
    			dy[I((5 + lmax + l), (5 + lmax + 0))] = -tdotaha10;
    			//dy[I((5 + lmax + l), (5 + lmax + 1))] = (k * l) / (a * ha * (2 * l + 1));
    			dy[I((5 + lmax + l), (5 + lmax + 1))] = kaha * l / (1 + 2 * l);
    			dy[I((5 + lmax + l), (5 + lmax + 2))] = 9 * tdotaha10;
    			//dy[I((5 + lmax + l), (5 + lmax + 3))] = -(k + k * l) / (a * ha * (2 * l + 1));
    			dy[I((5 + lmax + l), (5 + lmax + 3))] = -kaha * (1 + l) / (1 + 2 * l);
    		}

    		double dthetalm1 = 0;
    		double dthetalp1 = 0;
    		for (l = 3; l < lmax-1; l++) {
    			//dtheta L
    			//dy[I((5 + l), (5 + l - 1))] = (k * l) / (a * ha * (2 * l + 1));
    			dthetalm1 = kaha * l / (1 + 2 * l);
    			dy[I((5 + l), (5 + l - 1))] = dthetalm1;
    			dy[I((5 + l), (5 + l))] = tdotaha;
    			//dy[I((5 + l), (5 + l + 1))] = -(k + k * l) / (a * ha * (2 * l + 1));
    			dthetalp1 = -kaha * (1 + l) / (1 + 2 * l);
    			dy[I((5 + l), (5 + l + 1))] = dthetalp1;

    			//dtheta P L
    			//dy[I((5 + lmax + l), (5 + lmax + l - 1))] = (k * l) / (a * ha * (2 * l + 1));
    			dy[I((5 + lmax + l), (5 + lmax + l - 1))] = dthetalm1;
    			dy[I((5 + lmax + l), (5 + lmax + l))] = tdotaha;
    			//dy[I((5 + lmax + l), (5 + lmax + l + 1))] = -(k + k * l) / (a * ha * (2 * l + 1));
    			dy[I((5 + lmax + l), (5 + lmax + l + 1))] = dthetalp1;
    		}


    		double eta = computeEta(a);
    		
    		l = lmax - 1;
    		//dtheta lmax
    		//reset previously set values in this row
    		memset(&dy[I((5 + l), 0)], 0, len*sizeof(double));
    		dy[I((5 + l), (5 + l - 1))] = kaha;
    		dy[I((5 + l), (5 + l))] = 1 / (a * ha) * (-(l + 1) / eta + tdot);

    		//dtheta p lmax
    		//reset previously set values in this row
    		memset(&dy[I((5 + lmax + l), 0)], 0, len*sizeof(double));
    		dy[I((5 + lmax + l), (5 + lmax + l - 1))] = kaha;
    		dy[I((5 + lmax + l), (5 + lmax + l))] = 1 / (a * ha) * (-(l + 1) / eta + tdot);

    	}

    	#undef I
        return; 
    }
};
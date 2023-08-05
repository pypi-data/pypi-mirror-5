
//
// mdwt declarations
//
void MDWT(double *x, int m, int n, double *h0, double *h1, int lh, int L, double *y);

void fpsconv(double *x_in, int lx, double *h0, double *h1, int lhm1, 
	double *x_outl, double *x_outh);


//
// midwt declarations
//
void MIDWT(double *x, int m, int n, double *h0, double *h1, int lh, int L, double *y);

void bpsconv(double *x_out, int lx, double *g0, double *g1, int lhm1, 
	int lhhm1, double *x_inl, double *x_inh);


//
// mrdwt declarations
//
void
MRDWT(
    double *x,
    int m,
    int n,
    double *h0,
    double *h1,
    int lh,
    int L,
    double *yl,
    double *yh
    );

void fpconv(double *x_in, int lx, double *h0, double *h1, int lh,
       double *x_outl, double *x_outh);

//
// mirdwt declarations
//
void
MIRDWT(
   double *x,
   int m,
   int n,
   double *h0,
   double *h1,
   int lh,
   int L,
   double *yl,
   double *yh
   );

void bpconv(double *x_out, int lx, double *g0, double *g1, int lh,
       double *x_inl, double *x_inh);


//
// dwtaxis declarations
//
void
DWTAXIS(
    double *x,
    int n,
    int prod_h,
    int stride,
    double *h0,
    double *h1,
    int lh,
    int L,
    double *y
    );

void
IDWTAXIS(
    double *x,
    int n,
    int prod_h,
    int stride,
    double *h0,
    double *h1,
    int lh,
    int L,
    double *y
    );


# import profile
#
# Classes
#
class bspline(object):
    """Bspline class.

    Functions in the bspline library are implemented as methods on this
    class.
    """
    import numpy as np
    def __init__(self,x,**kwargs):
        """Init creates an object whose attributes are similar to the
        structure returned by the create_bspline function.
        """
        #
        # Default values
        #
        if 'nord' in kwargs:
            nord = kwargs['nord']
        else:
            nord = 4
        if 'npoly' in kwargs:
            npoly = kwargs['npoly']
        else:
            npoly = 1
        #
        # Set the breakpoints.
        #
        if 'bkpt' in kwargs and kwargs['bkpt'] is not None:
            bkpt = kwargs['bkpt']
        else:
            startx = x.min()
            rangex = x.max() - startx
            if 'placed' in kwargs:
                w = ((kwargs['placed'] >= startx) &
                    (kwargs['placed'] <= startx+rangex))
                if w.sum() < 2:
                    bkpt = self.np.arange(2,dtype='f')*rangex + startx
                else:
                    bkpt = kwargs['placed'][w]
            elif 'bkspace' in kwargs:
                nbkpts = int(rangex/kwargs['bkspace']) + 1
                if nbkpts < 2:
                    nbkpts = 2
                tempbkspace = rangex/float(nbkpts-1)
                bkpt = self.np.arange(nbkpts,dtype='f')*tempbkspace + startx
            elif 'nbkpts' in kwargs:
                nbkpts = kwargs['nbkpts']
                if nbkpts < 2:
                    nbkpts = 2
                tempbkspace = rangex/float(nbkpts-1)
                bkpt = self.np.arange(nbkpts,dtype='f')*tempbkspace + startx
            elif 'everyn' in kwargs:
                npkpts = max(nx/kwargs['everyn'], 1)
                if nbkpts == 1:
                    xspot = [0]
                else:
                    xspot = int(nx/(nbkpts-1))*self.np.arange(nbkpts,dtype='i4')
                bkpt = x[xspot].astype('f')
            else:
                raise ValueError('No information for bkpts.')
        imin = bkpt.argmin()
        imax = bkpt.argmax()
        if x.min() < bkpt[imin]:
            if 'silent' not in kwargs:
                print 'Lowest breakpoint does not cover lowest x value: changing.'
            bkpt[imin] = x.min()
        if x.max() > bkpt[imax]:
            if 'silent' not in kwargs:
                print 'Highest breakpoint does not cover highest x value: changing.'
            bkpt[imax] = x.max()
        nshortbkpt = bkpt.size
        fullbkpt = bkpt.copy()
        if 'bkspread' in kwargs:
            bkspread = kwargs['bkspread']
        else:
            bkspread = 1.0
        if nshortbkpt == 1:
            bkspace = bkspread
        else:
            bkspace = (bkpt[1] - bkpt[0]) * bkspread
        for i in range(1,nord):
            fullbkpt = self.np.insert(fullbkpt,0,bkpt[0]-bkspace*i)
            fullbkpt = self.np.insert(fullbkpt,fullbkpt.shape[0],
                bkpt[nshortbkpt-1] + bkspace*i)
        #
        # Set the attributes
        #
        nc = fullbkpt.size - nord
        self.breakpoints = fullbkpt
        self.nord = nord
        self.npoly = npoly
        self.mask = self.np.ones((fullbkpt.size,),dtype='bool')
        if npoly > 1:
            self.coeff = self.np.zeros((npoly,nc),dtype='d')
            self.icoeff = self.np.zeros((npoly,nc),dtype='d')
        else:
            self.coeff = self.np.zeros((nc,),dtype='d')
            self.icoeff = self.np.zeros((nc,),dtype='d')
        self.xmin = 0.0
        self.xmax = 1.1
        self.funcname = 'legendre'
        return
    #
    #
    #
    def fit(self,xdata,ydata,invvar,**kwargs):
        from pydlutils.bspline import cholesky_band, cholesky_solve
        if 'x2' in kwargs:
            x2 = kwargs['x2']
        else:
            x2 = None
        goodbk = self.mask[self.nord:]
        nn = goodbk.sum()
        if nn < self.nord:
            yfit = self.np.zeros(ydata.shape,dtype='f')
            return (-2,yfit)
        nfull = nn * self.npoly
        bw = self.npoly * self.nord
        a1,lower,upper = self.action(xdata,**kwargs)
        foo = self.np.tile(invvar,bw).reshape(bw,invvar.size).transpose()
        a2 = a1 * foo
        alpha = self.np.zeros((bw,nfull+bw),dtype='d')
        beta = self.np.zeros((nfull+bw,),dtype='d')
        bi = self.np.arange(bw,dtype='i4')
        bo = self.np.arange(bw,dtype='i4')
        for k in range(1,bw):
            bi = self.np.append(bi, self.np.arange(bw-k,dtype='i4')+(bw+1)*k)
            bo = self.np.append(bo, self.np.arange(bw-k,dtype='i4')+bw*k)
        for k in range(nn-self.nord+1):
            itop = k*self.npoly
            ibottom = min(itop,nfull) + bw - 1
            ict = upper[k] - lower[k] + 1
            if ict > 0:
                work = self.np.dot(a1[lower[k]:upper[k]+1,:].T,a2[lower[k]:upper[k]+1,:])
                wb = self.np.dot(ydata[lower[k]:upper[k]+1],a2[lower[k]:upper[k]+1,:])
                alpha.T.flat[bo+itop*bw] += work.flat[bi]
                beta[itop:ibottom+1] += wb
        min_influence = 1.0e-10 * invvar.sum() / nfull
        errb = cholesky_band(alpha,mininf=min_influence) # ,verbose=True)
        if isinstance(errb[0],int) and errb[0] == -1:
            a = errb[1]
        else:
            yfit,foo = self.value(xdata,x2=x2,action=a1,upper=upper,lower=lower)
            return (self.maskpoints(errb),yfit)
        errs  = cholesky_solve(a,beta)
        if isinstance(errs[0],int) and errs[0] == -1:
            sol = errs[1]
        else:
            yfit,foo = self.value(xdata,x2=x2,action=a1,upper=upper,lower=lower)
            return (self.maskpoints(errs),yfit)
        if self.npoly > 1:
            self.icoeff[:,goodbk] = self.np.array(a[0,0:nfull].reshape(self.npoly,nn),dtype=a.dtype)
            self.coeff[:,goodbk] = self.np.array(sol[0:nfull].reshape(self.npoly,nn),dtype=sol.dtype)
        else:
            self.icoeff[goodbk] = self.np.array(a[0,0:nfull],dtype=a.dtype)
            self.coeff[goodbk] = self.np.array(sol[0:nfull],dtype=sol.dtype)
        yfit,foo = self.value(xdata,x2=x2,action=a1,upper=upper,lower=lower)
        return (0,yfit)
    #
    #
    #
    def action(self,x,**kwargs):
        from pydl import uniq
        from pydlutils.goddard.math import fchebyshev, flegendre
        nx = x.size
        if 'x2' in kwargs and kwargs['x2'] is not None:
            if kwargs['x2'].size != nx:
                raise ValueError('Dimensions of x and x2 do not match.')
        nbkpt = self.mask.sum()
        if nbkpt < 2*self.nord:
            return (-2,0,0)
        n = nbkpt - self.nord
        gb = self.breakpoints[self.mask]
        bw = self.npoly*self.nord
        lower = self.np.zeros((n - self.nord + 1,),dtype='i4')
        upper = self.np.zeros((n - self.nord + 1,),dtype='i4') -1
        indx = self.intrv(x)
        bf1 = self.bsplvn(x, indx)
        action = bf1
        aa = uniq(indx,self.np.arange(indx.size,dtype='i4'))
        upper[indx[aa]-self.nord+1] = aa
        rindx = indx[::-1]
        bb = uniq(rindx,self.np.arange(rindx.size,dtype='i4'))
        lower[rindx[bb]-self.nord+1] = nx - bb - 1
        if 'x2' in kwargs and kwargs['x2'] is not None:
            x2norm = 2.0 * (kwargs['x2'] - sset['xmin']) / (sset['xmax'] - sset['xmin'] ) - 1.0
            if self.funcname == 'poly':
                temppoly = self.np.ones((nx,self.npoly),dtype='f')
                for i in range(1,self.npoly):
                    temppoly[:,i] = temppoly[:,i-1] * x2norm
            elif self.funcname == 'poly1':
                temppoly = self.np.tile(x2norm,self.npoly).reshape(nx,self.npoly)
                for i in range(1,self.npoly):
                    temppoly[:,i] = temppoly[:,i-1] * x2norm
            elif self.funcname == 'chebyshev':
                temppoly = fchebyshev(x2norm,self.npoly)
            elif self.funcname == 'legendre':
                temppoly = flegendre(x2norm,self.npoly)
            else:
                raise ValueError('Unknown value of funcname.')
            action = self.np.zeros((nx,bw),dtype='d')
            counter = -1
            for ii in range(self.nord):
                for jj in range(self.npoly):
                    counter += 1
                    action[:,counter] = bf1[:,ii]*temppoly[:,jj]
        return (action,lower,upper)
    #
    #
    #
    def intrv(self,x):
        gb = self.breakpoints[self.mask]
        n = gb.size - self.nord
        indx = self.np.zeros((x.size,),dtype='i4')
        ileft = self.nord -1
        for i in range(x.size):
            while x[i] > gb[ileft+1] and ileft < n - 1:
                ileft += 1
            indx[i] = ileft
        return indx
    #
    #
    #
    def bsplvn(self,x,ileft):
        bkpt = self.breakpoints[self.mask]
        vnikx = self.np.zeros((x.size,self.nord),dtype=x.dtype)
        deltap = vnikx.copy()
        deltam = vnikx.copy()
        j = 0
        vnikx[:,0] = 1.0
        while j < self.nord - 1:
            ipj = ileft+j+1
            deltap[:,j] = bkpt[ipj] - x
            imj = ileft-j
            deltam[:,j] = x - bkpt[imj]
            vmprev = 0.0
            for l in range(j+1):
                vm = vnikx[:,l]/(deltap[:,l] + deltam[:,j-l])
                vnikx[:,l] = vm*deltap[:,l] + vmprev
                vmprev = vm*deltam[:,j-l]
            j += 1
            vnikx[:,j] = vmprev
        return vnikx
    #
    #
    #
    def value(self,x,**kwargs):
        xsort = x.argsort()
        xwork = x[xsort]
        if 'x2' in kwargs and kwargs['x2'] is not None:
            x2work = kwargs['x2'][xsort]
        else:
            x2work = None
        if 'action' in kwargs:
            action = kwargs['action']
            lower = kwargs['lower']
            upper = kwargs['upper']
        else:
            action,lower,upper = self.action(xwork,x2=x2work)
        yfit = self.np.zeros(x.shape,dtype=x.dtype)
        bw = self.npoly * self.nord
        spot = self.np.arange(bw,dtype='i4')
        goodbk = self.mask.nonzero()[0]
        coeffbk = self.mask[self.nord:].nonzero()[0]
        n = self.mask.sum() - self.nord
        if self.npoly > 1:
            goodcoeff = self.coeff[:,coeffbk]
        else:
            goodcoeff = self.coeff[coeffbk]
        # maskthis = self.np.zeros(xwork.shape,dtype=xwork.dtype)
        for i in range(n-self.nord+1):
            ict = upper[i] - lower[i] + 1
            if ict > 0:
                yfit[lower[i]:upper[i]+1] = self.np.dot(
                    action[lower[i]:upper[i]+1,:],goodcoeff[i*self.npoly+spot])
        yy = yfit.copy()
        yy[xsort] = yfit
        mask = self.np.ones(x.shape,dtype='bool')
        gb = self.breakpoints[goodbk]
        outside = ((x < gb[self.nord-1]) |
            (x > gb[n]))
        if outside.any():
            mask[outside] = False
        hmm = ((self.np.diff(goodbk) > 2).nonzero())[0]
        for jj in range(hmm.size):
            inside = ((x >= self.breakpoints[goodbk[hmm[jj]]]) &
                (x <= self.breakpoints[goodbk[hmm[jj]+1]-1]))
            if inside.any():
                mask[inside] = False
        return (yy,mask)
    #
    #
    #
    def maskpoints(self,err):
        nbkpt = self.mask.sum()
        if nbkpt <= 2*self.nord:
            return -2
        hmm = err[self.np.unique(errb/self.npoly)]/self.npoly
        n = nbkpt - self.nord
        if self.np.any(hmm >= n):
            return -2
        test = self.np.zeros(nbkpt,dtype='bool')
        for jj in range(-self.np.ceil(nord/2.0),nord/2.0):
            foo = self.np.where((hmm+jj) > 0,hmm+jj,self.np.zeros(hmm.shape,dtype=hmm.dtype))
            inside = self.np.where((foo+nord) < n-1,foo+nord,self.np.zeros(hmm.shape,dtype=hmm.dtype)+n-1)
            test[inside] = True
        if test.any():
            reality = self.mask[test]
            if self.mask[reality].any():
                self.mask[reality] = False
                return -1
            else:
                return -2
        else:
            return -2


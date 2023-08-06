import warnings
import numpy as np
from scipy.stats.distributions import  t
from scipy.optimize import curve_fit, fsolve
from scipy.integrate import odeint

def regress(A, y, alpha=None):
    '''linear regression with conf intervals

    A is a matrix of function values in columns, e.g.
    A = np.column_stack([T**0, T**1, T**2, T**3, T**4])

    y is a vector of values you want to fit

    alpha is for the 100*(1 - alpha) confidence level

    This code is derived from the descriptions at http://www.weibull.com/DOEWeb/confidence_intervals_in_multiple_linear_regression.htm and http://www.weibull.com/DOEWeb/estimating_regression_models_using_least_squares.htm
    '''
    
    b, res, rank, s = np.linalg.lstsq(A, y)

    bint, se = None, None

    if alpha is not None:
        # compute the confidence intervals
        n = len(y)
        k = len(b)

        errors =  y - np.dot(A, b)
        sigma2 = np.sum(errors**2) / (n - k)  # RMSE

        covariance =  np.linalg.inv(np.dot(A.T, A))
                
        C = sigma2 * covariance 
        dC = np.diag(C)
        
        if (dC < 0.0).any():
            warnings.warn('\n{0}\ndetected a negative number in your'
                          'covariance matrix. Taking the absolute value'
                          'of the diagonal. something is probably wrong'
                          'with your data or model'.format(dC))
            dC = np.abs(dC)
            
        se = np.sqrt(dC) # standard error

        sT = t.ppf(1.0 - alpha/2.0, n - k - 1) # student T multiplier
        CI = sT * se

        bint = np.array([(beta - ci, beta + ci) for beta,ci in zip(b,CI)])

    return (b, bint, se)

def nlinfit(model, x, y, p0, alpha=0.05):
    '''nonlinear regression with conf intervals
    x is the independent data
    y is the dependent data
    model has a signature of f(x, p0, p1, p2, ...)
    p0 is the initial guess of the parameters
    '''
    pars, pcov = curve_fit(model, x, y, p0=p0)
    n = len(y)    # number of data points
    p = len(pars) # number of parameters

    dof = max(0, n - p) # number of degrees of freedom

    # student-t value for the dof and confidence level
    tval = t.ppf(1.0-alpha/2., dof) 

    SE = []
    pint = []
    for i, p,var in zip(range(n), pars, np.diag(pcov)):
        sigma = var**0.5
        SE.append(sigma)
        pint.append([p - sigma*tval, p + sigma*tval])

    return (pars, pint, SE)

def odelay(func, y0, xspan, events=[], TOLERANCE=1e-6, **kwargs):
    '''ode wrapper with events
    func is callable, with signature func(Y, x, *args)
    y0 are the initial conditions
    tspan  is what you want to integrate over

    events is a list of callable functions with signature event(Y, t, *args).
    These functions return zero when an event has happend.
    
    [value, isterminal, direction] = events(t,y)
    value(i) is the value of the ith event function.

    isterminal(i) = 1 if the integration is to terminate at a zero of
    this event function, otherwise, 0.

    direction(i) = 0 if all zeros are to be located (the default), +1
    if only zeros where the event function is increasing, and -1 if
    only zeros where the event function is decreasing.  
    '''

    x0 = xspan[0]  # initial point
#    xf = xspan[-1] # final point

#    f0 = func(y0, x0) # value of ode at initial point

    X = [x0]
    sol = [y0]
    TE, YE, IE = [], [], [] # where events occur
    
    # initial value of events
    e = np.zeros((len(events), len(xspan)))
    for i,event in enumerate(events):
        e[i,0], isterminal, direction = event(y0, x0)

    # now we step through the integration
    for i, x1 in enumerate(xspan[0:-2]):
        x2 = xspan[i + 1]
        f1 = sol[i]

        if 'full_output' in kwargs:
            f2, output = odeint(func, f1, [x1, x2], **kwargs)
            if output['message'] != 'Integration successful.':
                print output
        else:
            f2 = odeint(func, f1, [x1, x2], **kwargs)
        
        X += [x2]
        sol += [f2[-1][0]]

        #print X[-1], sol[-1], events[0](sol[-1], X[-1])

        # check event functions
        for j, event in enumerate(events):
            e[j, i + 1], isterminal, direction = event(sol[i + 1], X[i + 1])
                
            if ((e[j, i + 1] * e[j, i] < 0) 
                or np.abs(e[j, i + 1]) < TOLERANCE # this point is practically 0
                or np.abs(e[j, i]) < TOLERANCE):
                # change in sign detected Event detected where the sign of
                # the event has changed. The event is between xPt = X[-2]
                # and xLt = X[-1]. run a modified bisect function to
                # narrow down to find where event = 0
                xLt = X[-1]  # Last point
                fLt = sol[-1]
                eLt = e[j, i+1]

                xPt = X[-2]  # previous point
                fPt = sol[-2]
                ePt = e[j, i]

                k = 0 # bisection counter
                ISTERMINAL = False # assume this is the case
                # bisection loop
                while k < 100: # max iterations
                    if np.abs(xLt - xPt) < TOLERANCE:
                        # we know the interval to a prescribed precision now.
                        # check if direction is satisfied, and collect event if needed.
                        # e[j, i + 1] is the last value calculated
                        # e[j, i] is the previous to last
                        
                        COLLECTEVENT = False
                        # get all events
                        if direction == 0:
                            COLLECTEVENT = True
                        # only get event if event function is decreasing
                        elif (e[j, i + 1] > e[j, i] ) and direction == 1:
                            COLLECTEVENT = True
                        # only get event if event function is increasing
                        elif (e[j, i + 1] < e[j, i] ) and direction == -1:
                            COLLECTEVENT = True
                        else:
                            raise Exception, 'unexpected collectevent happened'
                            
                        if COLLECTEVENT:
                            TE.append(xPt)
                            YE.append(fPt)
                            IE.append(j)

                            if isterminal:
                                return X, sol, TE, YE, IE

                        break # and return to integrating

                    # slope of line connecting last and previous point
                    m = (ePt - eLt)/(xPt - xLt) # slope of line connecting points
                                                # bracketing zero

                    #estimated x where the zero is      
                    new_x = -ePt / m + xPt

                    # check if new_x is sufficiently different from xPt
                    if np.abs(new_x - xPt) < TOLERANCE:
                        # it is not different, so we do not go forward
                        xPt = xLt = new_x
                        continue                        

                    # now get the new value of the integrated solution at
                    # that new x
                    if 'full_output' in kwargs:
                        f, output  = odeint(func, fPt, [xPt, new_x], **kwargs)
                        if output['message'] != 'Integration successful.':
                            print output
                    else:
                        f  = odeint(func, fPt, [xPt, new_x], **kwargs)
                        
                    new_f = f[-1][-1]
                    new_e, isterminal, direction = event(new_f, new_x)

                    # now check event sign change
                    if ePt * new_e > 0:
                        xPt = new_x
                        fPt = new_f
                        ePt = new_e
                    else:
                        xLt = new_x
                        fLt = new_f
                        eLt = new_e

                    k += 1
                    
              
    return X, sol, TE, YE, IE


def deriv(x, y, method='two-point'):
    '''compute the numerical derivate dydx
    method = 'two-point': centered difference
             'four-point': centered 4-point difference
    '''
    x = np.array(x)
    y = np.array(y)
    if method == 'two-point':
        dydx = np.zeros(y.shape,np.float) #we know it will be this size
        dydx[1:-1] = (y[2:] - y[0:-2]) / (x[2:] - x[0:-2])

        # now the end points
        dydx[0] = (y[1] - y[0]) / (x[1] - x[0])
        dydx[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])
        return dydx

    elif method == 'four-point':
        dydx = np.zeros(y.shape, np.float) #we know it will be this size
        h = x[1] - x[0] #this assumes the points are evenely spaced!
        dydx[2:-2] = (y[0:-4] - 8 * y[1:-3] + 8 * y[3:-1] - y[4:]) / (12.0 * h)

        # simple differences at the end-points
        dydx[0] = (y[1] - y[0])/(x[1] - x[0])
        dydx[1] = (y[2] - y[1])/(x[2] - x[1])
        dydx[-2] = (y[-2] - y[-3]) / (x[-2] - x[-3])
        dydx[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])
        return dydx

    elif method == 'fft':
        # for this method, we have to start at zero.
        # we translate our variable to zero, perform the calculation, and then
        # translate back
        xp = np.array(x)
        xp -= x[0]
        
        N = len(xp)
        L = xp[-1]
        
        if N % 2 == 0:
            k = np.asarray(range(0, N / 2) + [0] + range(-N / 2 + 1,0))
        else:
            k = np.asarray(range(0,(N - 1) / 2) + [0] + range(-(N - 1) / 2, 0))

        k *= 2 * np.pi / L

        fd = np.fft.ifft(1.0j * k * np.fft.fft(y))
        return np.real(fd)



def bvp_L0(p, q, r, x0, xL, alpha, beta, npoints=100):
    '''solve the linear BVP with constant boundary conditions
    y'' + p(x)y' + q(x)y = r(x)
    y(x0) = alpha
    y(xL) = beta

    npoints is the number of discretizations. Two points count as the
    boundary values.
    '''

    h = (xL - x0) / (npoints - 3)
    X = np.linspace(x0 + h, xL - h, npoints - 2)
    
    # we do not do endpoints on A
    A = np.zeros((npoints - 2, npoints - 2))

    # special end point cases
    A[0][0] = -2.0 + h **2 * q(X[0])
    A[0][1] = 1.0 + h / 2.0 * p(X[0])
    A[-1][-2] = 1.0 - h / 2.0 * p(X[-1])
    A[-1][-1] = -2.0 + h**2 * q(X[-1])

    b = np.zeros(npoints - 2)
    b[0] = h**2 * r(X[0]) - alpha * (1.0 - h / 2.0 * p (X[0]))
    b[-1] =  h**2 * r(X[-1]) - beta * (1.0 - h / 2.0 * p (X[-1]))

    # now fill in the matrix
    for i in range(1, npoints - 3):          
        A[i][i-1] = 1.0 - h / 2.0 * p(X[i])
        A[i][i] = -2.0 + h**2 * q(X[i])
        A[i][i + 1] = 1 + h / 2.0 * p(X[i])

        b[i] = h**2 * r(X[i])

    # solve the equations
    y = np.linalg.solve(A, b)

    # add the boundary values back to the solution.
    return np.hstack([x0, X, xL]), np.hstack([alpha, y, beta])

def BVP_sh(F, x1, x2, alpha, beta, init):
    '''A shooting method to solve odes
    solve y'(x) = f(x, y)
    y(x1) = alpha
    y(x2) = beta

    y' is a system of ODES
    y1' = f(x, y1, y2)
    y2' = g(x, y1, y2)

    we know y1(0) = alpha

    init is your guess for y2(0)
    '''

    X = np.linspace(x1, x2)
    
    def objective(y20):
        y = odeint(F, [alpha, y20], X)
        y2 = y[:, 0]
        return beta - y2[-1]

    y20, = fsolve(objective, init)

    Y = odeint(F, [alpha, y20], X)
    return X, Y

def BVP_nl(F, X, BCS, init, **kwargs):
    '''solve nonlinear BVP y''(x) = F(x, y, y')
    
    X is a vector to make finite differences over

    BCS is a function that returns the boundary conditions: a,b = BCS(X, Y)
        
    init is a vector of initial guess
    '''

    x1, x2 = X[0], X[-1]
    N = len(X)
    h = (x2 - x1) / (N - 1)

    def residuals(y):
        '''When we have the right values of y, this function will be zero.'''

        res = np.zeros(y.shape)

        a,b = BCS(X, y)

        res[0] = a

        for i in range(1, N - 1):
            x = X[i]
            YPP = (y[i - 1] - 2 * y[i] + y[i + 1]) / h**2
            YP = (y[i + 1] - y[i - 1]) / (2 * h)
            res[i] = YPP - F(x, y[i], YP)

        res[-1] = b
        return res

    Y, something, flag, msg = fsolve(residuals, init, full_output=1)
    if flag != 1:
        print flag, msg
        raise Exception(msg)
    return Y


def bvp_sh(odefun, bcfun, xspan, y0_guess):
    '''
    solve Y' = f(Y, x) by shooting method

    bcfun(Ya, Yb)
    '''

    def objective(yinit):
        sol = odeint(odefun, yinit, xspan)
        res = bcfun(sol[0,:], sol[-1,:])
        return res

    Y0 = fsolve(objective, y0_guess)
    
    Y = odeint(odefun, Y0, xspan)
    return Y
    
def bvp(odefun, bcfun, X, yinit):
    '''
    solve Y' = f(Y, x)

    odefun is f(Y, x)
    bcfun is a function that returns the residuals at the boundary conditions, g(ya, yb)
    X is a grid to discretize the region
    yinit is a guess of the solution on that grid

    Example:
    ========
    y'' + |y| = 0
    y(0) = 0
    y(4) = -2
    
    def odefun(Y, x):
        y1, y2 = Y
        dy1dx = y2
        dy2dx = -np.abs(y1)
        return [dy1dx, dy2dx]

    def bcfun(Ya, Yb):
        y1a, y2a = Ya
        y1b, y2b = Yb

        return [y1a, -2 - y1b]

    x = np.linspace(0, 4, 100)

    y1 = 1.0 * np.ones(x.shape)
    y2 = 0.0 * np.ones(x.shape)

    Yinit = np.vstack([y1, y2])

    sol = bvp(odefun, bcfun, x, Yinit)
    '''
        
    def objective(Yflat):        
        Y = Yflat.reshape(yinit.shape)

        residbc = bcfun(Y[:,0], Y[:,-1])

        neq = len(Y) # number of equations
        nX = len(X)

        res = []

        # now the boundary conditions. We evaluate thise with 3-point formulas.
        # since these equations should be zero on both ends, we combine the two
        # equations to avoid overspecifying the problem.

        endpoints = []
        for j, val in enumerate(odefun(Y[:,0], X[0])):
            yjprime = (-3.0 * Y[j, 0] + 4.0 * Y[j, 1] - Y[j, 2]) / (X[2] - X[0])
            endpoints.append(yjprime - val)

        res += endpoints

        # now we need to loop through X and create equations
        for i in range(1, len(X) - 1):
            for j, val in enumerate(odefun(Y[:,i], X[i])):
                res.append((Y[j, i + 1] - Y[j, i - 1]) / (X[i + 1] - X[i - 1]) - val)

        res += residbc

        return res

    solflat = fsolve(objective, yinit.flat)

    sol = solflat.reshape(yinit.shape)
    
    return sol


if __name__ == '__main__':
    N = 101 #number of points
    L = 2 * np.pi #interval of data

    x = np.arange(0.0, L, L/float(N)) #this does not include the endpoint
    y = np.sin(x) + 0.05 * np.random.random(size=x.shape)

    dydx = deriv(x, y, 'fft')

    import matplotlib.pyplot as plt
    plt.plot(x, dydx, x, np.cos(x))
    plt.show()

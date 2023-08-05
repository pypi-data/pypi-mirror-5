from model import Model
from pySAXS.LS.LSsca import *
import numpy

class Triedra(Model):
    '''
    Cubes and parallelepiped
    by OS : 11/11/2011
    '''
    
    def PTriedre(self,q,par):
        """
        q array of q (A-1)
        par[0] side length  (in 1/q)
        par[1] thickness of the triedre (in 1/q)
        par[2] SLD particle (cm-2)
        par[3] SLD medium (cm-2)
        par[4] number density (cm-3)
        """        
        a = par[0]
        e=par[1]
        rho1 = par[2]
        rho2 = par[3]
        n=par[4]

        prefactor = 1e-48*n*(rho1-rho2)**2
        sign=[1,1,1,1,1]

        f = 3./16.*(e*a**2)**2*Pdqpoly(q,FaceTri(Triedre(a,e)),sign,24)
        return prefactor*f
    

    IntensityFunc=PTriedre #function
    N=0
    q=Qlogspace(3e-4,1.,50.)                             #q range(x scale)
    Arg=[30.,20.,9.8e11,9.8e10,1e10]                         #list of parameters
    Format=["%f","%f","%1.3e","%1.3e","%1.3e"]      #list of c format
    istofit=[True,True,False,False,False]           #list of boolean for fitting
    WarningForCalculationTime=False
    name="Not for fit: Triedra!"                      #name of the model
    Doc=["side length  ",\
         "thickness (in 1/q)",\
         "scattering length density of particle (cm-2)",\
         "scattering length density of medium (cm-2)",\
         "Number density (cm-3)"]           #list of description for parameters
    Description="Triedra "  # description of model
    Author="Olivier Spalla"                 #name of Author
    
if __name__=="__main__":
    '''
    test code
    '''
    modl=Triedra()
    #plot the model
    import Gnuplot
    gp=Gnuplot.Gnuplot()
    gp("set logscale xy")
    c=Gnuplot.Data(modl.q,modl.getIntensity(),with_='points')
    gp.plot(c)
    raw_input("enter") 
    #plot and fit the noisy model
    yn=modl.getNoisy(0.8)
    cn=Gnuplot.Data(modl.q,yn,with_='points')
    res=modl.fit(yn) 
    cf=Gnuplot.Data(modl.q,modl.IntensityFunc(modl.q,res),with_='lines')
    gp.plot(c,cn,cf)
    raw_input("enter")    
    #plot and fit the noisy model with fitBounds
    bounds=modl.getBoundsFromParam() #[250.0,2e11,1e10,1.5e15]
    res2=modl.fitBounds(yn,bounds)
    print res2
    raw_input("enter")  
    

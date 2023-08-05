from model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy
import scipy

class Fractal(Model):
    '''
    Fractal
    
    for Fractal Model
    by OT & CG 17/01/2012
    '''
    def FractalFunction(self,q,par):
        """
        Fractal model 
        par[0] : B2
        par[1] : Rg
        par[2] : Df
        """
        B2=par[0]
        Rg1=par[1]
        Df=par[2]
        Rg2=par[3]
        er1=scipy.special.erf(q*Rg1/(6.0**0.5))
        er2=scipy.special.erf(q*Rg2/(6.0**0.5))
        return B2*(q/er2**3)**-Df*(1-er1**2)
                
    
    
    IntensityFunc=FractalFunction #function
    N=0
    q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
    Arg=[1e-6,650,2.5,130]           #list of defaults parameters
    Format=["%1.3e","%1.3e","%1.3e","%1.3e"]      #list of c format
    istofit=[True,True,True,True]    #list of boolean for fitting
    name="Fractal"          #name of the model
    Doc=["B2",\
         "Rg agg",\
         "Fractal dimension",\
         "Rg prim"] #list of description for parameters
    specific=True  #for specific model, set to true
    Description="Fractal Model"  # description of model
    Author="OT & CG 17/01/2012"       #name of Author
    

from model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy

class Porod(Model):
    '''
    Porod
    
    for Porod Model
    by OT 10/06/2009
    '''
    def PorodFunction(self,q,par):
        """
        Porod model to fit q-4 part at high q
        par[0] : Scattering lenght density contrast in cm-2
        par[1] : S/V cm-1
        """
        return 2.0*numpy.pi*1.0e-32*par[0]*par[0]*par[1]*q**-4.0
            
    '''
    parameters definition
    class Model(7,Porod,/
    Qlogspace(1e-4,1.,500.),(
    [1.0e10,1e6]),
    ("Scattering contrast (cm-2)",
    "S/V (cm-1)"),("%1.3e","%1.3e"),
    (True,True)),
     
    
    from LSsca
    '''
    IntensityFunc=PorodFunction #function
    N=0
    q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
    Arg=[1.0e10,1e6]           #list of defaults parameters
    Format=["%f","%f","%1.3e","%1.3e","%1.3e"]      #list of c format
    istofit=[True,True]    #list of boolean for fitting
    name="Porod"          #name of the model
    Doc=["Scattering contrast (cm-2)",\
         "S/V (cm-1)"] #list of description for parameters
    
    
    
    
if __name__=="__main__":
    '''
    test code
    '''
    modl=Porod()
    #plot the model
    import Gnuplot
    gp=Gnuplot.Gnuplot()
    gp("set logscale xy")
    c=Gnuplot.Data(modl.q,modl.getIntensity(),with_='points')
    gp.plot(c)
    raw_input("enter") 
    #plot and fit the noisy model
    yn=modl.getNoisy(0.4)
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
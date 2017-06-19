class Point:
   def __init__(self, Geom1 = -10, E_tot = 10000, E_scf = 10000, E_corr = 0, Basis="", AugBasis="", TCutPNO=3.3e-7, TCutPairs=1.0e-4):
         self.Geom1 = Geom1
         self.E_tot = E_tot
         self.E_scf = E_scf
         self.E_corr = E_corr
         self.Basis = Basis
         self.AugBasis = AugBasis
         self.TCutPNO = TCutPNO
         self.TCutPairs = TCutPairs

   def CalcE_corr(self):
       self.E_corr = self.E_tot - self.E_scf


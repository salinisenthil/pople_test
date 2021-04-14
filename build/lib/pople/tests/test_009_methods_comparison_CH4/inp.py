import os
from pople import calculator as calc
from pople import au2kcm
from pople import HOF_atoms, dH_atoms
from pople import getatoms, uniqatoms, getmultip
import datetime , time

def enthalpy_form(geom, meth):

    start_time = time.time()
    
    exe='/home/Lib/ORCA_420/orca'

    out = calc(code='orca', code_exe=exe, method=meth, xyz=geom)

    HT_mol = out[2]
    U0_mol = out[0]
    
    #=== Atoms
    atoms = getatoms(geom)  # List of atoms
    
    uniq = uniqatoms(atoms) # Unique atom data
    
    N_ua = uniq["N_ua"]       # No. of unique atoms
    ua   = uniq["uniq_sym"]   # unique atoms
    ua_N = uniq["uan"]        # unique atom frequencies
    
    multip=getmultip(ua)    # Multiplicities of unique atoms
    
    U0_atoms_total=0        # Sum of internal energy (at 0 K) of atoms
    for i_ua in range(N_ua):
    
        print(' Atom ', ua[i_ua], ' with multiplicity ', multip[i_ua])
    
        #=== calculate for each unique atom
        geom = (f'''0  {multip[i_ua]} 
    {ua[i_ua]}  0.0 0.0 0.0 ''')
    
        out = calc(code='orca', code_exe=exe, method=meth, xyz=geom)
        U0=out[0]
    
        U0_atoms_total = U0_atoms_total + U0 * ua_N[i_ua] 
    
    
    U0molAE = U0_atoms_total-U0_mol # Atomization energy

    #=== Enthalpy of formation
    HT_form = HT_mol - U0_mol - U0molAE

    for i_ua in range(N_ua):

       HOF_0K     = HOF_atoms(ua[i_ua])
       dH_298K_0K = dH_atoms(ua[i_ua])
      
       HT_form = HT_form + ua_N[i_ua] * ( HOF_0K - dH_298K_0K )

    return(U0molAE, HT_form)




#=== Remove old files
os.system("rm -f ORCA.com ORCA.out Thermochemistry.out input.*")

#=== Two methods
methods=['g4mp2', 'g4mp2-xp']

#=== CH4 
geom = '''
 0  1
 C        0.00000000     0.00000000     0.00000000
 H        1.09336000     0.00000000     0.00000000
 H       -0.36445000     0.00000000    -1.03083000
 H       -0.36445000    -0.97188000     0.34361000
 H       -0.36445000     0.97188000     0.34361000
'''

AE=[]
HF=[]
ti=[]
for i in range(len(methods)):

    tic = time.time()
    val1,val2 = enthalpy_form(geom, methods[i])
    toc = time.time()

    AE.append(val1)
    HF.append(val2)
    ti.append(toc-tic)

print(" {:20s}{:20s}{:20s}{:20s}".format('Method','Atm. energy (kcal/mol)','Form. enthalpy (kcal/mol)','Time (sec)'))
for i in range(len(methods)):
    print(' {:20s}{:20.4f}{:20.4f}{:20.4f}'.format(methods[i], AE[i]*au2kcm, HF[i]*au2kcm,ti[i]))

#=== Reference output
#Method              Atm. energy (kcal/mol)Form. enthalpy (kcal/mol)Time (sec)          
#g4mp2                           392.2148            -17.6105            107.0206
#g4mp2-xp                        392.2910            -17.6868            181.7137
#Exp.                            397.94              -17.90

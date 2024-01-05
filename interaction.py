import math
import pandas as pd
import numpy as np

def generateInteractionPoints(D, b, cc, fck, fy, p, reinforcement_dist):
    '''
    D: Depth of section in mm
    b: Width of Section in mm
    cc: Clear cover in mm
    fck: Characteristics strength of concrete in MPa
    fy: Yield strength of steel in MPa
    p: Percentage of steel (p=1.2 if steel content is 1.2%)
    reinforcement_dist: Distribution of reinforcement. 
        0: Equally Distributed in each four side.
        1: Equally Discributed in two opposite side.
    '''
    Es = 2*10**5
    ast = p*D*b/100
    dia_of_tie = 8
    dia_of_tie = 8
    if reinforcement_dist==0:
        n_bars = 6+6+4+4
        dia_of_bar = math.sqrt(4*ast/(math.pi*n_bars))
        d1 = dia_of_tie + dia_of_bar/2 + cc
        d = 0.5*D-np.array([d1, (D-d1*2)*1/5+d1, (D-d1*2)*2/5+d1, (D-d1*2)*3/5+d1, (D-d1*2)*4/5+d1, (D-d1)])
        asti = np.array([6*ast/n_bars, 2*ast/n_bars, 2*ast/n_bars, 2*ast/n_bars, 2*ast/n_bars, 6*ast/n_bars])
    else:
        n_bars = 6+6
        dia_of_bar = math.sqrt(4*ast/(math.pi*n_bars))
        d1 = dia_of_tie + dia_of_bar/2 + cc
        d = np.array([0.5*D-d1, 0, 0, 0, 0, 0.5*D-(D-d1)])
        asti = np.array([6*ast/n_bars,0, 0, 0, 0, 6*ast/n_bars])



    data_steel_strain = []
    for i in np.arange(0.005,4.025,0.005):
        es = [i, 0,0,0,0,0,0]
        if i<=1.0:
            for j in range(1,7):
                es[j] = 0.0035*(i*D-0.5*D+d[j-1])/(i*D)
        else:
            for j in range(1,7):
                es[j] = 0.002*(i*D-0.5*D+d[j-1])/(i*D- 3*D/7)
        data_steel_strain.append(es)
    steel_strain_df = pd.DataFrame(data_steel_strain, columns=['xu/D', 'es1', 'es2', 'es3', 'es4', 'es5', 'es6'])


    def steel_stress(s):
        if s<0:
            return abs(max(-0.87*fy, s*Es))
        else:
            return min(0.87*fy, s*Es)

    fsi_df = pd.DataFrame(data_steel_strain, columns=['xu/D', 'fs1', 'fs2', 'fs3', 'fs4', 'fs5', 'fs6'])
    fsi_df['xu/D'] = steel_strain_df['xu/D']
    fsi_df['fs1'] = steel_strain_df['es1'].apply(steel_stress)
    fsi_df['fs2'] = steel_strain_df['es2'].apply(steel_stress)
    fsi_df['fs3'] = steel_strain_df['es3'].apply(steel_stress)
    fsi_df['fs4'] = steel_strain_df['es4'].apply(steel_stress)
    fsi_df['fs5'] = steel_strain_df['es5'].apply(steel_stress)
    fsi_df['fs6'] = steel_strain_df['es6'].apply(steel_stress)

    

    data_fci = []
    for i in np.arange(0.005,4.025,0.005):
        fc = [i, 0,0,0,0,0,0]
        for j in range(6):
            if 0.5*D-d[j]>=i*D:
                fc[j+1] = 0
            elif 0.5*D-d[j]<=3*D/7:
                fc[j+1] = 0.446*fck
            else:
                fc[j+1] = 0.446*fck - (0.446*fck*((0.5*D - d[j]-3*D/7)/(i*D-3*D/7))**2)
        data_fci.append(fc)

    fci_df = pd.DataFrame(data_fci, columns=['xu/D', 'fc1', 'fc2', 'fc3', 'fc4', 'fc5', 'fc6'])



    c_factors = []
    for i in np.arange(0.005,4.025,0.005):
        if i<=1:
            c1 = 0.446*(1-4/21)
            c2 = (0.446*0.5 - 8*0.446/49)/c1
        else:
            c1 = 0.446*(1-4*(4/(7*i-3))**2/21)
            c2 = (0.446*0.5 - 8*0.446*(4/(7*i-3))**2/49)/c1
        c_factors.append([i,c1,c2])

    c_factors_df = pd.DataFrame(c_factors, columns=['xu/D', 'c1', 'c2'])



    fac1 = []
    for i in range(len(data_steel_strain)):
        entry = [fci_df['xu/D'][i]]
        for j in range(6):
            if fci_df['xu/D'][i]*D <= D/2-d[j]:
                entry.append(asti[j]*(-fsi_df.iloc[i,j+1]-fci_df.iloc[i,j+1])/(b*D*fck))
            else:
                entry.append(asti[j]*(fsi_df.iloc[i,j+1]-fci_df.iloc[i,j+1])/(b*D*fck))

        fac1.append(entry)

    fac1_df = pd.DataFrame(fac1, columns=['xu/D', 'y1','y2', 'y3', 'y4', 'y5', 'y6'])


    fac2 = []
    for i in range(len(data_steel_strain)):
        entry2 = [fci_df['xu/D'][i]]
        for j in range(6):
            entry2.append(fac1_df.iloc[i,j+1]*d[j]/D)
        fac2.append(entry2)

    fac2_df = pd.DataFrame(fac2, columns=['xu/D', 'y1','y2', 'y3', 'y4', 'y5', 'y6'])



    p_m = []
    for i in range(len(data_steel_strain)):
        entry2 = [fci_df['xu/D'][i]]
        c1 = c_factors_df.iloc[i,1]
        c2 = c_factors_df.iloc[i,2]
        if fci_df['xu/D'][i]*D<=D:
            pu = fck*b*D*(c1*fci_df['xu/D'][i] + fac1_df.iloc[i,[1,2,3,4,5,6]].sum())/1000
            mu = fck*b*D*D*(c1*fci_df['xu/D'][i]*(0.5-c2*fci_df['xu/D'][i]) + fac2_df.iloc[i,[1,2,3,4,5,6]].sum())/1000000
        else:
            pu = fck*b*D*(c1 + fac1_df.iloc[i,[1,2,3,4,5,6]].sum())/1000
            mu = fck*b*D*D*(c1*(0.5-c2) + fac2_df.iloc[i,[1,2,3,4,5,6]].sum())/1000000
        entry2.append(pu)
        entry2.append(mu)
        p_m.append(entry2)

    p_m_df = pd.DataFrame(p_m, columns=['xu/D', 'Pu', 'Mu'])


    return p_m_df
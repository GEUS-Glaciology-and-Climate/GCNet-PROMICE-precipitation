#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Jan 17 2023

@author: jason box, GEUS

to output daily precipitation
to evaluate issues in precipitation data

"""


from datetime import datetime
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from numpy.polynomial.polynomial import polyfit
from datetime import date
import geopandas as gpd
from pyproj import Proj, transform
# from matplotlib import colors
from matplotlib.pyplot import figure
from PIL import Image
from pandas import Timestamp

th=2 # line thickness
formatx='{x:,.3f}' ; fs=16
plt.rcParams["font.size"] = fs
plt.rcParams['axes.facecolor'] = 'w'
plt.rcParams['axes.edgecolor'] = 'k'
plt.rcParams['axes.grid'] = False
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.8
plt.rcParams['grid.color'] = "#cccccc"
plt.rcParams["legend.facecolor"] ='w'
plt.rcParams["mathtext.default"]='regular'
plt.rcParams['grid.linewidth'] = th/2
plt.rcParams['axes.linewidth'] = 1
plt.rcParams['figure.figsize'] = 12, 20


if os.getlogin() == 'jason':
    base_path = '/Users/jason/Dropbox/AWS/GCNet-PROMICE-precipitation/'
    aws_data_path='/Users/jason/Dropbox/AWS/aws-l3/level_3/'
    aws_data_path='/Users/jason/0_dat/AWS/aws-l3/level_3/'

os.chdir(base_path)

today = date.today()
versionx= today.strftime('%Y-%m-%d')

# meta = pd.read_excel('/Users/jason/Dropbox/AWS/CARRA-TU_GEUS/metadata/IMEI_numbers_station_2021-10-27.xlsx')

meta = pd.read_csv('/Users/jason/0_dat/AWS/aws-l3/AWS_station_locations.csv')

meta = meta.rename({'stid': 'name'}, axis=1)
# fn='/Users/jason/Dropbox/AWS/PROMICE/ancil/PROMICE_info_all_2017-2018.csv'
# meta=pd.read_csv(fn)
print(meta.columns)

names=meta.name

do_plot=1
plt_elev_fit=0

# def pltovar(x,y,units,varname):
#     # ax.plot(y,'-o',label=varname)
#     units=units
#     varname=varname
    
#     v=np.where(y.values==np.nanmax(y.values))
#     print(x[v][0],y[v][0])
#     # v=y==np.nanmax(y)

#     # vv=[i for i, x in enumerate(v) if x]
#     # first_case=pd.to_datetime(x[vv[0]])
    
#     # s = pd.Series({Timestamp(str(first_case)): np.nanmax(y)})
#     # s.plot(ax=ax)
#     # ax.text(s.index[0], s.iloc[0], 'max: '+" %.1f" % np.nanmax(y)+' '+units)
#     # print(s.index[0], s.iloc[0])
    #

names=names[names!='Roof_PROMICE']
names=names[names!='Roof_GEUS']

do_plot=1

if do_plot:fig, ax = plt.subplots(figsize=(10,10))

for i,name in enumerate(names):
    if i>=0:
    # if name=='NUK_Uv3':
    # if name=='QAS_Uv3': # not added yet
    # if name=='QAS_L':
    # if name=='CP1':
    # if name=='DY2':
    # if name=='SWC':
    # if name=='SWC_O':
    # if name=='UPE_L':
    # if name=='JAR':
    # if name=='JAR_O':
    # if name=='SDM':
    # if name=='NUK_Uv3':

        print()
        print(i,name)#[i],meta.name[i],names[i][0:5])
        
        site=name

        fn=aws_data_path+site+'/'+site+'_hour.csv'
        fn=aws_data_path+site+'/'+site+'_day.csv'
        df=pd.read_csv(fn)        
        print(df.columns)
        # df.t_u
        # position
        n=20
        lat=np.nanmean(df.gps_lat[-n:])
        lon=-np.nanmean(df.gps_lon[-n:])
        elev=np.nanmean(df.gps_alt[-n:])
        print(site+", N %.3f" %lat+'°,W %.3f' %lon+', %.0f' %elev+' m')
        
        df.index = pd.to_datetime(df.time)
        
        iyear=2020
        fyear=2022
        # iyear=2022
        n_years=fyear-iyear+1
        
        issues_site=[]
        issues_date=[]
        issues_level=[]
        issues_p_rate=[]

        for yy,year in enumerate(np.arange(iyear,fyear+1)):
            
            flag=0
            if sum(df.columns=='t_l')==0:
                varnams=['precip_u','precip_u_cor','t_u']
            else:
                varnams=['precip_l','precip_l_cor','t_l','precip_u','precip_u_cor','t_u']
                flag=1
                
            temp=df.loc[(df['time'] >= str(year)+'-08-31') & (df['time'] <= str(year)+'-09-30')]
            temp=df.loc[(df['time'] >= str(year)+'-01-01') & (df['time'] <= str(year)+'-12-31')]
            tmpfile='/tmp/t'
            temp.to_csv(tmpfile,
                      columns = varnams)
            
            x=pd.read_csv(tmpfile)
            N=len(x)
            
            if N>0:
                x['tp_u']=np.nan
                for i in range(1,N):
                    x['tp_u'][i]=x['precip_u_cor'][i]-x['precip_u_cor'][i-1]
                    if x['tp_u'][i]>300 or x['tp_u'][i]<0:
                        issues_site.append(site)
                        issues_date.append(x.time[i])
                        issues_p_rate.append(x['tp_u'][i])
                        issues_level.append('u')
                        print('issue u ',x.time[i],x.time[i-1],x['precip_u_cor'][i],x['precip_u_cor'][i-1],x['tp_u'][i])
                        # x['tp_u'][i]=np.nan
                # x['precip_u_cor']-=np.nanmin(x['precip_u_cor'])
                # x['precip_u']-=np.nanmin(x['precip_u'])
                if flag:
                    x['tp_l']=np.nan
                    for i in range(1,N):
                        x['tp_l'][i]=x['precip_l_cor'][i]-x['precip_l_cor'][i-1]
                        if x['tp_l'][i]>300 or x['tp_l'][i]<0.:
                            issues_site.append(site)
                            issues_date.append(x.time[i])
                            issues_p_rate.append(x['tp_l'][i])
                            issues_level.append('l')
                            print('issue l ',x.time[i],x.time[i-1],x['precip_l_cor'][i],x['precip_l_cor'][i-1],x['tp_l'][i])
                            # x['tp_l'][i]=np.nan
                    # x['precip_l_cor']-=np.nanmin(x['precip_l_cor'])
                    # x['precip_l']-=np.nanmin(x['precip_l'])

                # print(x)
                countx=np.count_nonzero(~np.isnan(x['tp_u'].values))


                if np.nansum(x['tp_u'])!=np.nan:
                    # print('hi',countx)
                    if countx>0:
                        varnams=['time','precip_u','precip_u_cor','tp_u','t_u']
                        if flag:
                            varnams=['time','precip_l','precip_l_cor','tp_l','t_l','precip_u','precip_u_cor','tp_u','t_u']
                        x.to_csv('./output/'+site+'_'+str(year)+'.csv',
                                 columns=varnams,index=None, float_format="%.1f")
                        
                        if do_plot:
                            x.index = pd.to_datetime(x.time)
                            fig, ax = plt.subplots(figsize=(10,8))
                            ax.plot(x.tp_u, drawstyle='steps-mid',label='precip. rate from precip_l_cor')
                            if flag:
                                ax.plot(x.tp_l, drawstyle='steps-mid',label='precip. rate from precip_l_cor')
                            ax.set_ylabel('mm')
                            plt.legend()
                            plt.setp(ax.xaxis.get_majorticklabels(), rotation=90,ha='center' )
                            plt.title(site+' '+str(year))
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y %b %d'))
                            
                            ly='p'
                            
                            if ly == 'x':
                                plt.show()
                            
                            if ly == 'p':
                                figname='./Figs/'+site+'_'+str(year)+'.png'
                                plt.savefig(figname, bbox_inches='tight', dpi=100)
        if len(np.array(issues_site))>0:
            issues=pd.DataFrame(columns=['site','date','level','spurious_precip_rate'])
            issues['site']=pd.Series(np.array(issues_site))
            issues['date']=pd.Series(np.array(issues_date))
            issues['level']=pd.Series(np.array(issues_level))
            issues['spurious_precip_rate']=pd.Series(np.array(issues_p_rate))
            issues.to_csv('./issues/'+site+'.csv'
                         , float_format="%.1f",index=None)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 17:36:26 2022

@author: sx
"""
#%% set up
import pandas as pd
import datetime
path=('/Users/sx/Desktop/Carnegie Mellon University/data focused python/HW2/cme.20210709.c.pa2')
data=open(path)
datatxt=data.readlines()
#%%type selection
def select(data,location_start,location_end,letter):
    result=[]
    for x in data:
        if location_start==location_end:
            if x[location_start]==letter:
              result.append(x)  
        else:
            if x[location_start:location_end+1]==letter:
                result.append(x)
    return result
#%% slicing function
def sli(data,location_start,location_end):
    result=[]
    for x in data:
        result.append(x[location_start:location_end+1])
    return result
#%% change na to ''
def change_na(table):
    for i in range(0,table.shape[1]):
        table.iloc[:,i]=table.iloc[:,i].apply(lambda p: '' if pd.isna(p) else p)
    return table
#%% date selection
def date(table):
    table['Contract Month']=table['Contract Month'].apply(lambda p: p[:4]+'-'+p[4:6])
def longdate(table):
    table['Futures Exp Date']=table['Futures Exp Date'].apply(lambda p: p if p=='' else str(p))
    table['Futures Exp Date']=table['Futures Exp Date'].apply(lambda p: '' if p=='' else (p[:4]+'-'+p[4:6]+'-'+p[6:8]))
def dateselect(table):
    table['Contract Month']=table['Contract Month'].values.astype('datetime64')
    s_date=datetime.datetime.strptime('2021-09','%Y-%m')
    e_date=datetime.datetime.strptime('2023-12','%Y-%m')
    table=table[(table['Contract Month']>=pd.Timestamp(s_date))&(table['Contract Month']<=pd.Timestamp(e_date))].reset_index()
    table=table.drop(columns='index')
    table['Contract Month']=table['Contract Month'].apply(lambda p:p.strftime('%Y-%m'))
    return table    
#%% B type future
#extract all observations whose initial letter is B
type_B=select(datatxt,0,0,'B')
#extract all observations whose commodity code is CL
CL_type=select(type_B,2,7,'NYMCL ')
future_code=['CL'for i in range(len(CL_type))]
contract_month=sli(CL_type,18,23)
contract_type=['Fut'for i in range(len(CL_type))]
contract_exp_date=sli(CL_type,91,98)
up_list={'Futures Code':future_code,
         'Contract Month':contract_month,
         'Contract Type':contract_type,
         'Futures Exp Date':contract_exp_date
         }
#%% B type option
CL_oof=select(type_B,5,6,'LO')
#create a list includes future codes with the same size as the option_code
future_code=['CL'for i in range(len(CL_oof))]
#contract Month
contract_month=sli(CL_oof,18,23)
#make all elements in Contract Type 'Opt'
opt_contract_type=sli(CL_oof,5,6)
opt_contract_type=['Opt'for i in range(len(CL_oof))]
#Options Code
option_code=['LO' for i in range(len(CL_oof))]
#options expire date
options_exp_date=sli(CL_oof,91,98)

down_list={'Futures Code':future_code,
           'Contract Month':contract_month,
           'Contract Type':opt_contract_type,
           'Options Code':option_code,
           'Options Exp Date':options_exp_date
    }

#%%
table_1_up=pd.DataFrame(up_list)
table_1_down=pd.DataFrame(down_list)
#ignore_index help us to reset the index,otherwise the index will repeat itself.
#For example, we will have two index 0 in this dataframe!
table1=pd.concat([table_1_up,table_1_down],ignore_index=True)
table1=change_na(table1)
date(table1)
longdate(table1)
table1=dateselect(table1)
table1.sort_values(by=['Contract Month','Options Exp Date'])

#%% 81 type future
type_81=select(datatxt,0,1,'81')
CL_type_81=select(type_81,5,7,'CL ')
future_code=['CL'for i in range(len(CL_type_81))]
contract_month=sli(CL_type_81,29,34)
contract_type=['Fut'for i in range(len(CL_type_81))]
settlement_price=sli(CL_type_81,108,121)
settlement_price=[float(i[-4:])/100 for i in settlement_price]
up_list={'Futures Code':future_code,
         'Contract Month':contract_month,
         'Contract Type':contract_type,
         'Settlement Price':settlement_price
         }
#%%81 type option
option_type_81=select(type_81,15,17,'CL ')
option_type_81=select(option_type_81,25,27,'OOF')
future_code=['CL'for i in range(len(option_type_81))]
contract_month=sli(option_type_81,29,34)
#Call or put
contract_type=sli(option_type_81,28,28)
i=0
while i<len(contract_type):
    if contract_type[i]=='C':
        contract_type[i]='Call'
    else:
        contract_type[i]='Put'
    i+=1

strike_price=sli(option_type_81,47,53)
strike_price=[float(i[-2:])/100 for i in strike_price]
settlement_price=sli(option_type_81,108,121)
settlement_price=[float(i[-4:])/100 for i in settlement_price]
down_list={'Futures Code':future_code,
           'Contract Month':contract_month,
           'Contract Type':contract_type,
           'Strike Price':strike_price,
           'Settlement Price':settlement_price
    }

#%%
table_2_up=pd.DataFrame(up_list)
table_2_down=pd.DataFrame(down_list)
table2=pd.concat([table_2_up,table_2_down],ignore_index=True)
table_2=change_na(table2)
date(table2)
table2=dateselect(table2)
table2.sort_values(by='Contract Month')
#%%
table=pd.concat([table1,table2],ignore_index=True)
table=change_na(table)
table.to_csv('CL_expirations_and_settlements.txt',sep='\t',index=False)
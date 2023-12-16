import pandas as pd
import os
import numpy as np

# datapath = 'XXXX', set your data path
os.chdir(datapath)

### For those seeking additional details about this dataset, 
### please refer to the following reference: 
### https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

##########data clean and processing
# Read the data from 'online_retail_II.xlsx' file
tran_df = pd.read_excel('online_retail_II.xlsx')

## use info() for EDA
info_eda = tran_df.info()

def data_mata_eda(DF,key):
    # DF,key = tran_df.copy(), 'key'
    d_types = DF.dtypes.reset_index() 
    d_types.columns = ['col', 'dtype']
    d_missing = DF.isnull().sum().reset_index() 
    d_missing.columns = ['col', 'missing_n']
    d_missing['missing_per'] = round(100*d_missing['missing_n'] / len(DF), 2) 
    c = list(DF.columns)
    vc_lst = []
    for v in c:
        d_cat = DF[v].value_counts()
        level_n = len(d_cat)
        vc = [v, level_n]
        vc_lst.append(vc)
        
    cntlev_df = pd.DataFrame(vc_lst, columns = ['col', 'cat_levels'])    
    dflist = [d_types, d_missing, cntlev_df]
    df_all = cosemerge(dflist, ['col'], 'inner')
    key_u = len(DF[key].unique())
    df_all['uniq_key_num'] = key_u
    df_all['row_num'] = len(DF)
    df_all['col_num'] = len(c)
    return df_all 

def contain_keys(keys, lst):
    x = True
    for it in keys:
        if (it in lst) == False:
            x = False
    return x        
           
def cosemerge(dflist, keys, stymerge):
    k = 0    
    res_df = pd.DataFrame([])
    for tem_df in dflist:
        if k==0: res_df = tem_df.copy()
        else: 
            a_in = contain_keys(keys, list(res_df.columns))
            b_in = contain_keys(keys, list(tem_df.columns))
            if len(tem_df) > 0 and len(res_df) > 0 and a_in and b_in: 
                res_df = pd.merge(tem_df, res_df, on = keys, how = stymerge)
        k = k + 1
    return res_df


tran_df = pd.read_excel('online_retail_II.xlsx')

cols = ['Invoice', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'Price']
tran_df[cols].head(8)

# define unique kyy
tran_df['key'] = tran_df['Invoice'].astype(str) + tran_df['StockCode'].astype(str) + \
                 tran_df['Description'].astype(str) +  tran_df['Quantity'].astype(str) +\
                 tran_df['InvoiceDate'].astype(str)

#run eda function                 
eda_res1 = data_mata_eda(tran_df,'key')
# compare with info() 
tran_df.info()

###########################################################
d_types = tran_df.dtypes
numerics = ['int16', 'int32', 'int64', 
            'float16', 'float32', 'float64',
            'bool', 'uint8']

d_types_df = d_types.reset_index()
d_types_df.columns = ['var','dtype']
d_types_df['dtype'] = d_types_df['dtype'].astype(str)

##get lists that holds variable names with the different data types
obj_var = d_types_df[d_types_df.dtype.isin(['object'])]['var'].tolist()
num_var = d_types_df[d_types_df.dtype.isin(numerics)]['var'].tolist()
dt_var = d_types_df[d_types_df.dtype.isin(['datetime64[ns]'])]['var'].tolist()

####################for obj data##################################
def obj_eda(df, obj_var):
# Initialize an empty result DataFrame
    df_res = pd.DataFrame()

    # Iterate through each column ('a' and 'b') in the DataFrame
    for col in obj_var:
        # Extract column data
        col_data = df[col]
        # Calculate the maximal text string length
        max_length = col_data.str.len().max()
        # Calculate the minimal text string length
        min_length = col_data.str.len().min()
        # Count the number of categorical levels (unique text strings)
        num_levels = col_data.nunique()
        num_levels_lw = col_data.str.lower().nunique()
        # Count the number of observations that can be converted into numeric
        num_numeric = pd.to_numeric(col_data, errors='coerce').notnull().sum()
        # Count the number of observations that can be converted into datetime or date
        num_datetime = pd.to_datetime(col_data, errors='coerce').notnull().sum()
        # Count the number of missing values
        missing_cnt = col_data.isnull().sum()
        # Check for ',' or whitespace in each row
        cnt_comma_whitespace = col_data.str.contains(',|\\s').sum()
        # Create a dictionary for the current column's EDA results
        col_result = {
            'col_name': col,
            'max_length': max_length,
            'min_length': min_length,
            'num_levels': num_levels,
            'num_levels_lw' : num_levels_lw,
            'num_numeric': num_numeric,
            'num_datetime': num_datetime,
            'missing_cnt': missing_cnt,
            'cnt_comma_whitespace': cnt_comma_whitespace
        }

        # Append the dictionary to the result DataFrame
        df_res = df_res.append(col_result, ignore_index=True)
        df_res['row_n'] = df.shape[0]
        df_res['col_n'] = df.shape[1]

    return df_res

res_obj_df = obj_eda(tran_df, obj_var)

cols =   ['col_name',  'max_length', 'min_length',
       'num_levels',   'num_numeric', 'num_levels_lw',
       'num_datetime',  'missing_cnt']
res_obj_df[cols]

#################for datetime data#####################
def date_eda(df, dt_var):
    df_res = pd.DataFrame()
    for col in dt_var:
        col_data = df[col]
        max_date = col_data.max()
        min_date = col_data.min()
        num_datetime_levels = col_data.nunique()
        date_formats = col_data.dt.date.astype(str).unique()
        num_date_formats = len(date_formats)
        avg_days_to_max_date = (max_date - col_data).dt.days.mean()
        std_days_to_max_date = (max_date - col_data).dt.days.std()
        days = (max_date - min_date).days
        
        col_result = {
            'col_name': col,
            'max_date': max_date,
            'min_date': min_date,
            'days':days,
            'num_datetime_levels': num_datetime_levels,
            'num_uniq_date': num_date_formats,
            'avg_days_to_max_date': round(avg_days_to_max_date, 1),
            'std_days_to_max_date': round(std_days_to_max_date, 1)
        }
        df_res = df_res.append(col_result, ignore_index=True)
        df_res['row_n'] = df.shape[0]
        df_res['col_n'] = df.shape[1]
    return df_res


result_df = date_eda(tran_df, dt_var)
cols = ['col_name', 'max_date', 'days', 'num_datetime_levels',
      'avg_days_to_max_date', 'num_uniq_date']
      
result_df[cols]

#################for numeric data#####################
def numeric_eda(df, num_vars):
    df_res = pd.DataFrame()
    for col in num_vars:
        col_data = df[col]
        mean_value = col_data.mean()
        max_value = col_data.max()
        min_value = col_data.min()
        num_levels = col_data.nunique()
        median_value = col_data.median()
        q1_value = col_data.quantile(0.25)
        q3_value = col_data.quantile(0.75)
        iqr_value = q3_value - q1_value
        lower_bound = q1_value - 1.5 * iqr_value
        upper_bound = q3_value + 1.5 * iqr_value
        outliers_low = (col_data < lower_bound).sum()
        outliers_high = (col_data > upper_bound).sum()
        std_value  = col_data.std()
        col_result = {
            'col_name': col,
            'mean_value' : mean_value,
            'max_value': max_value,
            'min_value': min_value,
            'num_levels': num_levels,
            'median_value': median_value,
            'Q1': q1_value,
            'Q3': q3_value,
            'IQR': iqr_value,
            'lower_bound' : lower_bound,
            'upper_bound' : upper_bound,
            'outliers_low': outliers_low,
            'outliers_high': outliers_high,
            'std':std_value
        }
        df_res = df_res.append(col_result, ignore_index=True)
        df_res['row_n'] = df.shape[0]
        df_res['col_n'] = df.shape[1]
    return df_res


result_df = numeric_eda(tran_df, num_var)
cols= ['col_name', 'mean_value', 'std', 'lower_bound', 'upper_bound', 
      'outliers_low', 'outliers_high']

result_df[cols]

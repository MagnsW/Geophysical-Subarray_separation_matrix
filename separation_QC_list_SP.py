
# coding: utf-8

# In[1]:


import glob
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns


# ## Automatic QC Based on String Separation TXT File

# Reading in subarray separation txt file to dataframe

# In[2]:


stat_data_file = input("Specify modeled data filename (csv format): ")


# In[3]:


#stat_data_file = "modeling_output.txt"


# In[4]:


stat_data_clean = pd.DataFrame()


# In[5]:


stat_data_clean = pd.read_csv(stat_data_file)


# In[6]:


#stat_data_clean


# In[7]:


separation_file = input("Specify filename for subarray separations: ")


# In[8]:


#separation_file = "seq0104_substring_separation.txt"


# In[9]:


separation_data = pd.DataFrame()


# In[10]:


separation_data = pd.read_csv(separation_file, skiprows=1, delim_whitespace=True)


# In[11]:


#separation_data


# Plotting Subarray separation per shot:

# In[12]:


sns.set_style("darkgrid")
plt.figure(figsize=(17,12))
sns.regplot(x=separation_data["shotpno"], y=separation_data["arr1_2"], fit_reg=False, label="arr1-2")
sns.regplot(x=separation_data["shotpno"], y=separation_data["arr2_3"], fit_reg=False, label="arr2-3")
plt.legend();


# Rounding and making separations format compatible with modeled data dataframe:

# In[13]:


def format_separation(x):
    y = x*2
    y = round(y)
    y = y*5
    return y


# In[14]:


separation_data["Separation S1-S2"] = separation_data["arr1_2"].apply(lambda x: format_separation(x))
separation_data["Separation S2-S3"] = separation_data["arr2_3"].apply(lambda x: format_separation(x))


# In[15]:


separation_data


# Merging separation data with modeled data:

# In[16]:


separation_data_merge = separation_data.merge(stat_data_clean, how='inner', left_on=['Separation S1-S2', 'Separation S2-S3'], right_on=['Separation S1-S2', 'Separation S2-S3']).sort_values(by=['shotpno']).reset_index().drop(['index', 'Farfield Name'], axis=1)


# In[17]:


separation_data_merge


# Plotting shots and their legal label. There are two separate legal labels, one for x-correlation (green, yellow, red) and one based on dropout (binary)

# In[18]:


def plot_shots(shotno, sep12, sep23, legal, title):
    plt.figure(figsize=(17, 12))
    sns.set_style("darkgrid")
    color = legal
    plt.scatter(shotno, sep12, c=color)
    plt.scatter(shotno, sep23, c=color)
    plt.xlabel("Shot point number")
    plt.ylabel("Subarray separation (dm)")
    plt.title(title)
    plt.show()


# In[19]:


plot_shots(separation_data_merge["shotpno"], separation_data_merge["Separation S1-S2"], separation_data_merge["Separation S2-S3"], separation_data_merge["X-corr Legal"], "X-correlation criteria")


# In[20]:


def plot_shots_xcorr(shotno, xcorr, legal, title):
    plt.figure(figsize=(17, 12))
    sns.set_style("darkgrid")
    color = legal
    plt.scatter(shotno, xcorr, c=color)
    plt.xlabel("Shot point number")
    plt.ylabel("X-correlation")
    plt.axhline(0.998, color='black', linestyle='dashed')
    plt.axhline(0.995, color='black', linestyle='dashed')
    plt.title(title)
    plt.show()


# In[21]:


plot_shots_xcorr(separation_data_merge["shotpno"], separation_data_merge["X-corr"], separation_data_merge["X-corr Legal"], "X-correlation criteria" )


# In[22]:


sep_data_xcorr_flagged = separation_data_merge[separation_data_merge["X-corr Legal"] != 'green']


# In[23]:


plot_shots_xcorr(sep_data_xcorr_flagged["shotpno"], sep_data_xcorr_flagged["X-corr"], sep_data_xcorr_flagged["X-corr Legal"], "X-correlation criterial - Flagged only")


# In[24]:


sep_data_xcorr_flagged = sep_data_xcorr_flagged.reset_index().drop('index', axis=1)


# In[25]:


sep_data_xcorr_flagged['test'] = sep_data_xcorr_flagged['shotpno'] - sep_data_xcorr_flagged.index*2


# In[26]:


#sep_data_xcorr_flagged.head(40)


# In[27]:


minvals = sep_data_xcorr_flagged.groupby(['test', 'X-corr Legal']).min().reset_index()[['test', 'shotpno', 'X-corr Legal']]


# In[28]:


countvals = sep_data_xcorr_flagged.groupby(['test', 'X-corr Legal']).count().reset_index()[['test', 'shotpno']].rename(columns={'shotpno': 'Count'})


# In[29]:


output = minvals.join(countvals, rsuffix="-r").drop(['test', 'test-r'], axis=1).sort_values('shotpno').reset_index().drop('index', axis=1)


# In[30]:


outputfilename = "SP_flagged_" + separation_file
output.to_csv(outputfilename, sep=',', index=False)


from Scheduler import Job
from Scheduler import loadYAML
import plotly.express as px
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
# from pandas.api.types import (
#     is_categorical_dtype,
#     is_datetime64_any_dtype,
#     is_numeric_dtype,
#     is_object_dtype,
# )
from streamlit_option_menu import option_menu

#layout page
tab1, tab2, tab3 = st.tabs(["Read Me", "Job Menu", "Job Scheduler"])

with tab1:
   st.header("Read Me")
   st.image("https://static.streamlit.io/examples/cat.jpg", width=200)

with tab2:
   st.header("Job Menu")
   st.write(
    """Load and view a menu of jobs the job shop can manufacture.
    Start by uploading a yaml file that defines the different job options
    """
    )

with tab3:
   st.header("Job Scheduler")
   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

YAML_path = r"C:\Users\bella\PythonScheduler\job_config.yaml"

df_w = loadYAML(YAML_path)

#update dataframe
ls_proctime_idletime_tuples, ls_proctime_plus_idletime, ls_total_work_seq_time= [], [], []
for idx, row in df_w.iterrows():
    inst_name = row["name"]
    inst_name = Job(
    row["name"],
    row["id"], 
    row["work_sequence"],
    row["cost_dollars"], 
    row["treatment_sequence"]
    )

    df_w["treatment_sequence"][idx] = inst_name.treatment_sequence

    print(inst_name.id)
    ls_total_work_seq_time.append(sum(inst_name.ls_proctime_plus_idletime))
    ls_proctime_idletime_tuples.append(inst_name.ls_proctime_idletime_tuples)
    ls_proctime_plus_idletime.append(inst_name.ls_proctime_plus_idletime)

df_w["proctime_idletime_tuples"] = ls_proctime_idletime_tuples
df_w["proctime_plus_idletime"] = ls_proctime_plus_idletime
df_w["total_work_seq_time"] = ls_total_work_seq_time # in minutes
print(df_w)

# set class variables
Job.set_num_shifts(df_w["num_shifts"][0])
Job.set_workday(df_w["num_hrs_per_workday"][0])
print("num shifts", Job.set_num_shifts)
print("num shifts", Job.set_workday) # workday in hours

# find max number of jobs per shift
df_w["max_num_jobs_per_shift"] = ((Job.num_hrs_per_workday/Job.num_shifts)*60) / df_w["total_work_seq_time"]
print(df_w)

#plot stacked column
# fig = px.bar(df_w, x='name', y='cost_dollars')
# fig.show()

# fig = px.bar(df_w, x="num_shifts", y="total_work_seq_time", color="total_work_seq_time", title="Long-Form Input")
# fig.show()

# shift_len_minus_total_work_seq_time_in_min = (Job.num_hrs_per_workday*60/ Job.num_shifts) - df_w["total_work_seq_time"].sum()

# if (shift_len_minus_total_work_seq_time_in_min) <0:
#     print("shift boundary exceeded by %s minutes. " % shift_len_minus_total_work_seq_time_in_min)

# print(df_w["total_work_seq_time"].sum())

# print("percent of %s-hour workday left to schedule: " % Job.num_hrs_per_workday)
# print(round((df_w["total_work_seq_time"].sum() / (Job.num_hrs_per_workday *60))*100, 1))

# make copy of dataframe to drop/add rows user selects
df_w_edit = df_w.copy()

# drop rows from dataframe
def drop_rows(idx):
    # argument is index of the row to drop. Drops row inplace 
    df_w_edit.drop(idx, inplace=True)

# add rows to dataframe
def add_rows(colname, colval):
    # arguments are col name and col value of df_w row to add
    # reset index after adding column
    df_to_add = df_w[df_w[colname]== colval]
    df_w_edit = pd.concat([df_w_edit, df_to_add])
    df_w_edit.reset_index(inplace=True, drop=True)
    
# reindex rows in dataframe
def reindex_df(ls_new_order):
    #argument is list of new order of rows by index
    df_w_edit = df_w_edit.reindex(ls_new_order)
    return df_w_edit

# export as csv
def export_df_as_csv():
    df_export = pd.DataFrame()
    for idx, row in df_w_edit.iterrows():
        inst_name = row["name"]
        inst_name = Job(
        row["name"],
        row["id"], 
        row["work_sequence"],
        row["cost_dollars"], 
        row["treatment_sequence"]
        )

        df_export_single = inst_name.make_single_job_schedule()
        df_export = pd.concat([df_export, df_export_single])
        # path = r"C:\Users\bella\Desktop\export_%s.csv"  %self.name
        # df_export.to_csv(path, index=False)

    print(df_export.head())



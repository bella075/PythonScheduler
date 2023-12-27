from Scheduler import Job
from Scheduler import loadYAML
from Scheduler import add_calculated_col_to_yaml_data
import plotly.express as px
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import yaml
from streamlit_option_menu import option_menu

#FUNCTIONS
# set class variables for number of shifts and number of hours per workday
def set_class_variables():
    Job.set_num_shifts(df_j["num_shifts"][0])
    Job.set_workday(df_j["num_hrs_per_workday"][0])

# drop rows from dataframe
def drop_rows(idx):
    # argument is index of the row to drop. Drops row inplace 
    df_j_edit.drop(idx, inplace=True)

# add rows to dataframe
def add_rows(colname, colval):
    # arguments are col name and col value of df_j row to add
    # reset index after adding column
    df_to_add = df_j[df_j[colname]== colval]
    df_j_edit = pd.concat([df_j_edit, df_to_add])
    df_j_edit.reset_index(inplace=True, drop=True)
    
# reindex rows in dataframe
def reindex_df(ls_new_order):
    #argument is list of new order of rows by index
    df_j_edit = df_j_edit.reindex(ls_new_order)
    return df_j_edit

# export as csv
def export_df_as_csv():
    df_export = pd.DataFrame()
    for idx, row in df_j_edit.iterrows():
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

    return df_export

#layout page
tab0, tab1, tab2 = st.tabs(["Read Me", "Job Menu", "Job Scheduler"])

#session state variables
if 'job_menu' not in st.session_state:
    st.session_state['job_menu'] = pd.DataFrame()
with tab0:
    st.write(
    '''
    Job Class Description:

    Each instance of a job will have, at minimum:
    name -> string
    id -> string
    work_seq_str -> work sequence to complete a job. A string of processing times and downtimes in minutes for a given work sequence.
        A work sequence can have one process or many processes. If there is more than one process in the seuqence, then
        processing times will be separated by a "-" delimiter. Processing time includes setup time, but does not include
        downtime. If idle time is required after process, p, then a "/" delimtier will follow the 
        processing time and the idle time,i, will be given. Idle time may be required if job needs to cool or set before
        commencing the next step inthe work sequence.
            Example: 20-10/3-10/4. The second process takes 10 minutes and 3 minutes of idle time are required.
        The total time the job consumes for the workstation will be the processing time + idle time 
    cost_dollars -> includes labor and material cost for a job

    Some jobs may require special treatments. If a series of treatments are required, it is assummed that the
    treatments specified will be applied sequentially for all work sequences. 
    The entirety of the treatment must be applied within a pre-defined fixed amount of of time.
    If there are more treatments than processes then, the sequence of processes will repeat until all treatments are applied.
    '''
    )

with tab1:
    st.header("Job Menu")

    st.subheader("Upload Jobs")
    st.write("Upload a YAML file that defines the jobs your job shop can manufacture.")
    # YAML_path = r"C:\Users\bella\PythonScheduler\job_config.yaml"

    YAML_path = st.file_uploader('Choose a YAML file')
    # st.write(YAML_path)
    # read and restructure temps data
    if YAML_path:
        df_j_init = loadYAML(YAML_path)
        st.session_state.job_menu = df_j_init
        with st.expander("View uploaded jobs"):
            st.dataframe(st.session_state.job_menu)
        st.subheader("Job Menu")
        df_j_full = add_calculated_col_to_yaml_data(df_j_init)
        df_j = df_j_full[["name", "id", "cost_dollars", 
            "treatment_sequence", "proctime_idletime_tuples",
            "proctime_plus_idletime", "total_work_seq_time", "num_shifts"]]
        st.dataframe(df_j)

    st.subheader("Visualize Jobs")
    if YAML_path:
        
        col0, col1, col2 = st.columns(3)
        with col0:
            st.write("Workday Metrics  :sunglasses:")
            st.button("Set class variables", on_click=set_class_variables)
        col1.metric("Work Shifts / Day", df_j_full["num_shifts"][0], delta=None)
        col2.metric("Work Hours / Day", df_j_full["num_hrs_per_workday"][0], delta=None)

        #plot stacked column
        fig_cost = px.bar(df_j, x='name', y='cost_dollars')
        st.plotly_chart(fig_cost, use_container_width=True)

        fig = px.bar(df_j, x='name', y='cost_dollars')
        st.plotly_chart(fig, use_container_width=True)
       
        
with tab2:
    st.header("Job Scheduler")
    if YAML_path:
        st.dataframe(df_j)

        # # find max number of jobs per shift
        df_j["max_num_jobs_per_shift"] = ((Job.num_hrs_per_workday/Job.num_shifts)*60) / df_j["total_work_seq_time"]
        print(df_j)

        #plot stacked column
        fig_bar = px.bar(df_j, x="num_shifts", y="total_work_seq_time", color="total_work_seq_time", title="Long-Form Input")
        st.plotly_chart(fig_bar, use_container_width=True)

# shift_len_minus_total_work_seq_time_in_min = (Job.num_hrs_per_workday*60/ Job.num_shifts) - df_j["total_work_seq_time"].sum()

# if (shift_len_minus_total_work_seq_time_in_min) <0:
#     print("shift boundary exceeded by %s minutes. " % shift_len_minus_total_work_seq_time_in_min)

# print(df_j["total_work_seq_time"].sum())

# print("percent of %s-hour workday left to schedule: " % Job.num_hrs_per_workday)
# print(round((df_j["total_work_seq_time"].sum() / (Job.num_hrs_per_workday *60))*100, 1))

# make copy of dataframe to drop/add rows user selects
# df_j_edit = df_j.copy()



from Scheduler import Job
from Scheduler import loadYAML
from Scheduler import add_calculated_col_to_yaml_data
import plotly.express as px
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import yaml
import plotly.graph_objects as go
# from bokeh.models import ColumnDataSource
# from bokeh.plotting import figure, show

#FUNCTIONS
# set class variables for number of shifts and number of hours per workday
def set_class_variables():
    Job.set_num_shifts(df_j_full["num_shifts"][0])
    Job.set_workday(df_j_full["num_hrs_per_workday"][0])

# drop rows from dataframe
def drop_rows(idx):
    # argument is index of the row to drop. Drops row inplace 
    st.session_state.user_sel_jobs.drop(idx, inplace=True)
    st.session_state.user_sel_jobs.reset_index(inplace=True, drop=True)

# add rows to dataframe
def add_rows(colname, colval):
    # arguments are col name and col value of df_j row to add
    # reset index after adding column
    df_to_add = df_j[df_j[colname]== colval]
    st.session_state.user_sel_jobs = pd.concat([st.session_state.user_sel_jobs, df_to_add])
    st.session_state.user_sel_jobs.reset_index(inplace=True, drop=True)
    
# reindex rows in dataframe
def reindex_df(ls_new_order):
    #argument is list of new order of rows by index
    df_j_edit = df_j_edit.reindex(ls_new_order)
    return df_j_edit

# preview export as csv
def preview_export_df_as_csv(df_input):
    df_export = pd.DataFrame()
    print(df_input.shape)
    time_now = 0
    for idx, row in df_input.iterrows():
        # inst_name = row["name"]
        inst_name = Job( row["name"],
        row["id"], 
        row["work_sequence"],
        row["cost_dollars"], 
        row["treatment_sequence"])
        df_export_single = inst_name.make_single_job_schedule(start_time=time_now)
        time_now = df_export_single.iloc[-1]["toa_at_work_station"] + df_export_single.iloc[-1]["process_time_sec"]
        print("log", idx, row["name"], time_now)
        df_export = pd.concat([df_export, df_export_single])
    return df_export

#export as csv    
def export_df_as_csv(df, path):
        #path = r"C:\Users\bella\Desktop\export_%s.csv" 
        path = path
        df.to_csv(path, index=False)
        return df
# layout page
# st.set_page_config(layout="wide")
tab1, tab2 = st.tabs(["Job Menu", "Schedule Jobs"])

#session state variables
if 'job_menu' not in st.session_state:
    st.session_state['job_menu'] = pd.DataFrame()
if 'user_sel_jobs' not in st.session_state:
    st.session_state['user_sel_jobs'] = pd.DataFrame()
if 'drop_or_add' not in st.session_state:
    st.session_state['drop_or_add'] = None
if 'job_to_add' not in st.session_state:
    st.session_state['job_to_add'] = None
if 'job_to_drop' not in st.session_state:
    st.session_state['job_to_drop'] = None
if 'submit' not in st.session_state:
    st.session_state['submit'] = None
if 'reset' not in st.session_state:
    st.session_state['reset'] = None
if 'shift_current_delta' not in st.session_state:
    st.session_state['shift_current_delta'] = 0
if 'demo_data' not in st.session_state:
    st.session_state['demo_data'] = None
if 'preview_schedule' not in st.session_state:
    st.session_state['preview_schedule'] = None

with tab1:
    st.header("Upload & Visualize Job Menu")

    st.subheader("Upload Jobs")
    st.write("Upload a YAML file that defines the jobs your job shop can manufacture.")
    # YAML_path = r"C:\Users\bella\PythonScheduler\job_config.yaml"

    YAML_path = st.file_uploader('Choose a YAML file')
    st.write("File path:", YAML_path)
    
     # add option to preview app with demo data
    st.write('''
        **Want to preview the app without loading your own defined job options?**
             
        Toggle the switch below to populate the job menu with some default job options. 
        Untoggle to switch the app to a mode that requires a user-provided yaml file.
             ''')
    st.session_state['demo_data'] = st.toggle('Preview the app with default job options')
    if st.session_state['demo_data']:
        YAML_path = r"job_config.yaml"
        st.write("Load default job options.")
    
    #give option to upload demo
    if YAML_path:
        df_j_init = loadYAML(YAML_path)
        st.session_state.job_menu = df_j_init
        with st.expander("View jobs without calculated columns"):
            st.dataframe(st.session_state.job_menu)
        st.subheader("Full Job Menu")
        df_j_full = add_calculated_col_to_yaml_data(df_j_init)
        df_j = df_j_full[["name", "id", "cost_dollars", "work_sequence",
            "treatment_sequence", "proctime_idletime_tuples",
            "proctime_plus_idletime", "total_work_seq_time", "num_shifts"]]
        st.dataframe(df_j_full)
      
        
    
    if (YAML_path):
        st.subheader("Set Number of Shifts and Workday Durations")
        col0, col1, col2 = st.columns(3)
        st.write('''Parameters from the your selected job configuration file are shown below.
            Click below to set these as class variables that will apply to all job instances.
            Note: It is assummed that all shifts in a workday have the same duration.''')
        with col0:
            st.button("Click here to set parameters as class variables",
             on_click=set_class_variables)
        col1.metric("Work Shifts / Day", df_j_full["num_shifts"][0], delta=None)
        col2.metric("Work Hours / Day", df_j_full["num_hrs_per_workday"][0], delta=None)
        st.subheader("Visualize Jobs")
        #plot stacked column
        fig_cost = px.bar(df_j, x='name', y='cost_dollars', title= "Job Cost ($) ").update_layout(
            xaxis_title="Job Name", yaxis_title="Unit Cost ($)")
        st.plotly_chart(fig_cost, use_container_width=True)

        sel_job_to_graph = st.selectbox("Select a job to graph", list(df_j_full["name"].values))
        if sel_job_to_graph:
            tups = df_j_full[df_j_full["name"]== sel_job_to_graph]["proctime_idletime_tuples"].values[0]
            ptimes, idletimes, opnum = [], [], []
            st.write(tups)
            st.write("total work sequence time for",
                sel_job_to_graph," is ",
                df_j_full[df_j_full["name"]== sel_job_to_graph]["total_work_seq_time"].values[0], " minutes")
            for count, t in enumerate(tups):
                ptimes.append(float(t[0]))
                idletimes.append(float(t[1]))
                opnum.append("operation_%s" %count)

        # processing and idle time graph
        fig_pi_time = go.Figure()
        fig_pi_time.add_trace(go.Bar(x=opnum, y=ptimes,
                        base=0,
                        marker_color='crimson',
                        name='processing time'
                        ))
        fig_pi_time.add_trace(go.Bar(x=opnum, y=idletimes,
                        base=[-1*x for x in idletimes],
                        marker_color='lightslategrey',
                        name='idle time'))
        fig_pi_time.update_layout(title="Work Sequence Time (minutes)")
        st.plotly_chart(fig_pi_time, use_container_width=True)

       #bokeh plot
        # source = ColumnDataSource(df_j)
        # p = figure( title='simple line example',
        #     x_axis_label='Name',
        #     y_axis_label='Cost in Dollars')
        # p.vbar(x='name', top='cost_dollars', width=0.9, legend_field="name", source=source)
        # st.bokeh_chart(p, use_container_width=True)
        
with tab2:
    st.header("Schedule Jobs")
    if not YAML_path:
        st.write("Upload a job menu to schedule jobs.")
    if YAML_path:
        st.subheader("Job Menu")
        st.dataframe(df_j)

        # # find max number of jobs per shift
        df_j["max_num_jobs_per_shift"] = ((
            Job.num_hrs_per_workday/Job.num_shifts)*60) / df_j["total_work_seq_time"]
        print(df_j)

        st.subheader("Make Schedule")
        col0, col1 = st.columns(2)

        #line below will reset user_sel_jobs each time submit button clicked!
        #st.session_state.user_sel_jobs = pd.DataFrame(columns = df_j.columns)
        with col0:
            #select to perform a drop or add action
            st.session_state.drop_or_add = st.radio(
            "Do you wish to drop or add a job? ",
            [":red[DROP]", ":green[ADD]"], index=None,)  
        with col1:
            if st.session_state.drop_or_add:
                # provide list of indices for user to select which to drop
                if st.session_state.drop_or_add == ":red[DROP]":
                    if len(list(st.session_state.user_sel_jobs.index)) == 0:
                        st.write("There are currently no jobs scheduled.")
                    st.session_state.job_to_drop = st.selectbox(
                        "select the index for the row you wish to %s" %st.session_state.drop_or_add,
                        tuple(list(st.session_state.user_sel_jobs.index))
                        )
                    st.write("You selected to ", st.session_state.drop_or_add,
                              "the job with index", st.session_state.job_to_drop)
                    st.write("Click the Submit button to drop the job from your schedule.")
                    
                # select which job from the menu to add 
                elif st.session_state.drop_or_add == ":green[ADD]":
                    st.session_state.job_to_add = st.selectbox(
                        "Select a job to %s " %st.session_state.drop_or_add, 
                        tuple(df_j["name"].values)
                        )
                    st.write("You selected to ", st.session_state.drop_or_add, st.session_state.job_to_add)
                    st.write("Click the Submit to add the job to your schedule.")
                    
                st.session_state.submit = st.button("Submit", type="primary")
        
        # if submit button is clicked, update df
        if st.session_state.submit:
            # update shift and total work seq time delta
            #st.session_state.shift_current_delta = (Job.num_hrs_per_workday*60/ Job.num_shifts) - st.session_state.user_sel_jobs["total_work_seq_time"].sum()
           
            if (st.session_state.drop_or_add is not None) and (st.session_state.job_to_add is not None):
                # add selected rows
                if st.session_state.drop_or_add == ":green[ADD]":
                    add_rows("name", st.session_state.job_to_add)
                # drop selected rows
                elif st.session_state.drop_or_add == ":red[DROP]":
                    st.write(st.session_state.job_to_drop)
                    drop_rows(st.session_state.job_to_drop)
                    #st.session_state.user_sel_jobs(st.session_state.job_to_drop)

        st.subheader("Current Schedule")
        st.write(st.session_state.user_sel_jobs)
        col_barplot1, col_barplot2 = st.columns(2)
        with col_barplot1:
            st.subheader("Time Consumption")
            if len(list(st.session_state.user_sel_jobs.index)) > 0:
                # plot stacked column of current schedule and bar chart to viz shift time and workday time
                fig_bar = px.bar(st.session_state.user_sel_jobs, x="num_shifts", y="total_work_seq_time", color="total_work_seq_time", text = "name", title=" Total Time (minutes) in Current Schedule ")
                st.plotly_chart(fig_bar, use_container_width=True)
        with col_barplot2:
            st.subheader("Metrics (in Minutes)")
            if len(list(st.session_state.user_sel_jobs.index)) > 0:
                st.write("Total time consumed by jobs selected:", st.session_state.user_sel_jobs["total_work_seq_time"].sum())
                st.write("Workday duration:", Job.num_hrs_per_workday * 60)
                st.write("Single shift duration:", (Job.num_hrs_per_workday * 60 / Job.num_shifts) )
        
        st.subheader("Export Schedule")
        # display only if jobs are scheduled
        if (len(list(st.session_state.user_sel_jobs.index)) == 0):
            st.write("No jobs scheduled.")
        else:
            st.write('''
                    The exported schedule will include the time of arrival (TOA) of each
                    job at each workstation specified in the job's work sequence.
                    ''')
            st.session_state.preview_schedule = st.button("Click to preview schedule before export")
            if st.session_state.preview_schedule:
                df_to_export = st.session_state.user_sel_jobs
                st.dataframe(preview_export_df_as_csv(df_to_export))

            # if export, iterate over df to apply method "make single job schedule" from Job class
            export_path = st.text_input("Provide the directory path for your export. If the csv file does not already exist, create a blank csv file at the location first.")
            
            st.write("**Path example:**", r"C:\Users\bella\Desktop\my_schedule.csv")
            st.write("File path for exported schedule:", export_path)
            #export and reset buttons
            col2, col3 = st.columns(2)
            with col2:
                export_as_csv = st.button("Export schedule as csv")
            with col3:
                st.session_state.reset = st.button("Clear ALL jobs from schedule")
                st.write("Double click to clear table displayed above.")
            if export_path:
                df_to_export = preview_export_df_as_csv(st.session_state.user_sel_jobs)
                df_exported = export_df_as_csv(df_to_export, export_path)
                st.write("Preview of exported schedule")
                st.write(df_exported.head())
                st.write(st.session_state.user_sel_jobs)
                
        # if reset, clear df
        if st.session_state.reset:
            st.session_state.user_sel_jobs = pd.DataFrame(columns = df_j.columns)
            st.write(st.session_state.user_sel_jobs)


# shift_current_delta = (Job.num_hrs_per_workday*60/ Job.num_shifts) - df_j["total_work_seq_time"].sum()


# print(df_j["total_work_seq_time"].sum())

# print("percent of %s-hour workday left to schedule: " % Job.num_hrs_per_workday)
# print(round((df_j["total_work_seq_time"].sum() / (Job.num_hrs_per_workday *60))*100, 1))

# make copy of dataframe to drop/add rows user selects
# df_j_edit = df_j.copy()



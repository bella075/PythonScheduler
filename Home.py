import streamlit as st

st.header("Home")

st.markdown('''
**Purpose:**  The purpose of this app is to assist a job shop with scheduling production.
            
**Background:**  A job shop manufactures custom products in small quantities based on customer orders.
            ''') 

with st.expander("**Job Requirements**"):
    st.markdown(
        '''
        **Job Requirements**: Each instance of a job will have, at minimum, a name, ID, and a work sequence.
        A work sequence can have one or more operations.
        Every operation in a work sequence will have a processing time, given in minutes.
        Processing time includes setup time, but does not include idle time. Idle time may be required after an operation
        if the widget being manufactured needs to cool or set before
        commencing the next step in its work sequence. 
    
        :rainbow[To get started, load a YAML file with job requirements for each unique job. 
        This will be used to create the menu of jobs you can choose from when creating your schedule.] 

        **Job Configuration Descriptions:**

        **:red[name]** -> type: string

        **:red[id]** -> type: string

        **:red[cost_dollars]** -> type: float. includes labor and material cost for a job

        **:red[work_seq_str]** -> type: string. A string of processing times and idle times in minutes for a given work sequence.
    
        > If there is more than one process in the seqence, 
        then processing times will be separated by a "-" delimiter. If idle time is required after an operation, then a "/" delimiter will follow the 
        processing time, p, and the idle time,i, will be given.

        > EXAMPLE: "20-10/3-10/4". The second process takes 10 minutes and 3 minutes of idle time are required.
        The total time the job consumes for the workstation will be the processing time + idle time 

        **:red[treatment_sequence]** -> type: float. If a job requires a series of treatments, it is assummed that the
        treatments specified will be applied sequentially for all work sequences. 

        > If there are more treatments than processes, then once the treatment is applied to the last operation in a 
        > work sequence, it will move on the the first operation and traverse the work sequence as many times as needed to complete
        the full sequence. Use the "-" delimiter to delineate treatments. If no treatment is required,
        enter: "0" in the YAML file. EXAMPLE: "20-40-50".

        **YAML File Example:**
        This example file can be found here: https://github.com/bella075/PythonScheduler

        Go to the Job Scheduler page (expand the menu on the left if hidden) to load jobs and begin scheduling!
        '''
        )
with st.expander("**Job Configuration Screenshot**"):
    st.image('ConfigExample.png', caption='Screenshot of YAML file example.')

with st.expander("**Enhancement Backlog**"):
    st.write('''
    Enhancement #1 : Give ERROR message when a shift boundary or work-day boundary is crossed.
             
    >Description: Currently, the onus falls on the user to ensure they do not schedule jobs that cross 
        shift or work day boundaries. This can be done using the following metrics displayedin the job
        scheduler: the cummulative time consumed by scheduled jobs, shift duration, and  work-day duration.
        This enhancement would automatically check boundaries are not crossed each time a job is dropped/added.
             
    Enhancement #2: Add GUI to create or edit an existing job configuration file.    
    
    ''')
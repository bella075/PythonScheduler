import pandas as pd 
import yaml
from pathlib import Path  

# Job shop scheduler 
class Job:
    num_unique_jobs = 0
    num_hrs_per_workday = 21
    num_shifts = 3
    num_hrs_per_shift = num_hrs_per_workday / num_shifts #assume equal shifts

    '''
    Each job will have, at minimum:
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

    def __init__(self, name, id, work_sequence, cost_dollars, treatment_sequence=None):
        self.name = name
        self.id = id  
        self. work_sequence = work_sequence 
        self.cost_dollars = cost_dollars
        self.treatment_sequence = treatment_sequence
        self.treatment_sequence = Job.convert_treatment_seq_string_to_list(self)
        self.ls_proctime_idletime_tuples = Job.combine_processing_and_idle_times(self)[0]
        self.ls_proctime_plus_idletime = Job.combine_processing_and_idle_times(self)[1]
        self.min_num_job_req_for_full_treatment = Job.min_num_job_req_for_full_treatment(self)

    num_unique_jobs += 1

    @classmethod
    def set_workday(cls,num_hrs_per_workday):
        cls.num_hrs_per_workday = num_hrs_per_workday
        cls.num_hrs_per_shift = cls.num_hrs_per_workday / cls.num_shifts
        
    @classmethod
    def set_num_shifts(cls, num_shifts):
        cls.num_shifts = num_shifts
        cls.num_hrs_per_shift = cls.num_hrs_per_workday / cls.num_shifts

    def combine_processing_and_idle_times(self):
        # group processing and recovery times
        ls_proctime_idletime_tuples = []
        ls_proctime_plus_idletime = []

        ptimes = self.work_sequence.split("-")
        for count, p in enumerate(ptimes):
            p = p.split("/")
            print(len(p))
            if len(p) == 2:
                ls_proctime_idletime_tuples.append((float(p[0]), float(p[1])))
                ls_proctime_plus_idletime.append(float(p[0])+ float(p[1]))
            elif len(p) == 1:
                ls_proctime_idletime_tuples.append((float(p[0]), 0))
                ls_proctime_plus_idletime.append(float(p[0]))
            else:
                print("error!")
            # print("proc and idle tuples", ls_proctime_idletime_tuples)
            # print("list of proc plus idle", ls_proctime_plus_idletime)
        return ls_proctime_idletime_tuples, ls_proctime_plus_idletime
    
    def min_num_job_req_for_full_treatment(self):
        if (len(self.treatment_sequence) / len(self.ls_proctime_plus_idletime)) > 1:
            min_num_job_req_for_full_treatment = int((len(self.treatment_sequence) / len(self.ls_proctime_plus_idletime)))
        else: 
            min_num_job_req_for_full_treatment = 1
        return min_num_job_req_for_full_treatment

    @staticmethod
    def min_to_sec(x):
        return float(x)*60
    
    @staticmethod
    def hours_to_min(x):
        return float(x)*60
    
    # convert treatement sequence from string to list
    def convert_treatment_seq_string_to_list(self):
        if self.treatment_sequence == "0":
            self.treatment_sequence = [0]
        else:
            self.treatment_sequence = self.treatment_sequence.split("-")
        return self.treatment_sequence
    
    def make_single_job_schedule(self, start_time):
        ls_toa, ls_process_time, ls_shift_counter, ls_job_counter = [], [], [], []
        ls_day_counter, ls_cost_dollars, ls_treatment_sequence= [], [], []
        elapsed_time = start_time
        shift_counter, day_counter, treatment_counter = 1, 1, 0

        #update treatment_sequence
        print("treatment_sequence", self.treatment_sequence)

        for w in range(self.min_num_job_req_for_full_treatment):
            for count, tup in enumerate(self.ls_proctime_idletime_tuples):
                if count == 0:
                    ls_process_time.append(tup[0])
                    ls_toa.append(elapsed_time)
                else:
                    ls_process_time.append(tup[0])
                    ls_toa.append(elapsed_time)

                elapsed_time = elapsed_time + tup[0] + tup[1]
                ls_shift_counter.append(shift_counter)
                ls_day_counter.append(day_counter)
                ls_cost_dollars.append(self.cost_dollars)
                ls_job_counter.append(w)

                if self.treatment_sequence == "0":
                    ls_treatment_sequence.append(0)
                elif treatment_counter < len(self.treatment_sequence):
                    ls_treatment_sequence.append(self.treatment_sequence[treatment_counter])
                    treatment_counter +=1
                else:
                    treatment_counter = 0 #restart counter
                    ls_treatment_sequence.append(self.treatment_sequence[0])

        columns = ["toa_at_work_station", "process_time_sec", "job_counter", "shift_counter", "day_counter", "cost_dollars", "treatment_sequence"]
        data = list(zip(ls_toa, ls_process_time, ls_shift_counter, ls_job_counter, ls_day_counter, ls_cost_dollars, ls_treatment_sequence ))

        df_export= pd.DataFrame(columns=columns, data=data)
        return df_export
    
    def export_single_job_schedule_as_csv(self):
        df_export = Job.make_single_job_schedule(self)
        path = r"C:\Users\bella\Desktop\export_%s.csv"  %self.name
        print(path)
        # print(df_export)
        df_export.to_csv(path, index=False)
        return df_export
    
def add_calculated_col_to_yaml_data(df_j):
    # takes as an argument the dataframe created from user's yaml file and returned from loadYAML()
    ls_proctime_idletime_tuples, ls_proctime_plus_idletime, ls_total_work_seq_time= [], [], []
    for idx, row in df_j.iterrows():
        inst_name = row["name"]
        inst_name = Job(
        row["name"],
        row["id"], 
        row["work_sequence"],
        row["cost_dollars"], 
        row["treatment_sequence"]
        )

        print(inst_name.id)
        ls_total_work_seq_time.append(sum(inst_name.ls_proctime_plus_idletime))
        ls_proctime_idletime_tuples.append(inst_name.ls_proctime_idletime_tuples)
        ls_proctime_plus_idletime.append(inst_name.ls_proctime_plus_idletime)

    df_j["proctime_idletime_tuples"] = ls_proctime_idletime_tuples
    df_j["proctime_plus_idletime"] = ls_proctime_plus_idletime
    df_j["total_work_seq_time"] = ls_total_work_seq_time # in minutes
    return df_j
    
def loadYAML(YAML_path):
    try:
        with open(YAML_path) as stream:
            data = yaml.safe_load(stream)
    except:
        data = yaml.safe_load(YAML_path)
  
    data["num_hrs_per_workday"]
    print(data["num_shifts"])
    
    print(data["published"])
    df_j = pd.DataFrame.from_dict(data["job"])
    df_j["num_hrs_per_workday"] = data["num_hrs_per_workday"]
    df_j["num_shifts"] = data["num_shifts"]
    df_j["published"] = data["published"]
    print(df_j)
    return df_j

if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.

    job_1 = Job("Job1", "J234", "40-20/10-30/20-80-50", 100, "100-75-50-25")
    # job_2 = Job("Job2", "J234", "30-40", 100, None)

    print(job_1.name, job_1.id, job_1.work_sequence, job_1.treatment_sequence)
   
    # job_1.export_single_job_schedule_as_csv()
    # print(issubclass(Job_with_Treatment, Job)) 
    # print(isinstance(job_1, Job))

    # print(job_1.combine_processing_and_idle_times())

    # print(job_1.__dict__)
    # print(job.num_unique_jobs)
    # print(Job.set_workday(27))
    # print(Job.num_hrs_per_workday)
    # print(job_1.num_hrs_per_workday)
    # print(job_1.num_hrs_per_shift)

    # YAML_path = r"C:\Users\bella\PythonScheduler\job_config.yaml"
    # df_j = loadYAML(YAML_path)

    



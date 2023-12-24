import pandas as pd 

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
    processing_time_string -> string of times in minutes to perform a sequence of processes for a job.
        A job can have one process or many processes. If a job requires several processes, then
        processing time(s) will be separated by a "-" delimiter and listed in sequential order.
    recovery time_string-> string of times in minutes to clean/reconfigure after each process. 
        Each process in a job must have exactly one specified recovery time value. For instance,
        if there are 5 processes, then 5 recovery times MUST be specified (even if recovery time is 0)
    cost_dollars -> includes labor and material cost for jobs

    Some jobs may require special treatments. If a series of treatments are required for a job, it is assummed that the
    treatments specified will be applied sequentially to all processes in the job. 
    The entirety of the treatment must be applied within a pre-defined fixed amount of of time.
    If there are more treatments than processes then, the sequence of processes will repeat until all treatments are applied.
    '''

    def __init__(self, name, id, processing_time, recovery_time, cost_dollars, treatment_sequence=None):
        # self.type = "short"
        self.name = name
        self.id = id  
        self.processing_time = processing_time 
        self.recovery_time = recovery_time 
        self.cost_dollars = cost_dollars
        self.treatment_sequence = treatment_sequence

        Job.num_unique_jobs += 1

    @classmethod
    def set_workday(cls,num_hrs_per_workday):
        cls.num_hrs_per_workday = num_hrs_per_workday
        cls.num_hrs_per_shift = cls.num_hrs_per_workday / cls.num_shifts
        
    @classmethod
    def set_num_shifts(cls, num_shifts):
        cls.num_shifts = num_shifts
        cls.num_hrs_per_shift = cls.num_hrs_per_workday / cls.num_shifts

    def group_p_r_times(self):
        # group processing and recovery times
        ls_grouped_times = []
        ptimes = self.processing_time.split("-")
        rtimes = self.recovery_time.split("-")
        if len(ptimes) == len(rtimes):
            for count, p in enumerate(ptimes):
                ls_grouped_times.append((p, rtimes[count]))
        else:
            print(
                ''' processing times and recovery times mismatch. 
                Make sure the number of processing and recovery times are equal
                '''
                )
        return ls_grouped_times
    

    def min_to_sec(self):
        pass
    
# class Job_with_Treatment(Job):
#     '''
#     Each job will have, at minimum:
#     if a series of treatments are required for a job, it is assummed that the
#     treatments specified will be applied sequentially to all processes in the job.
#     The entirety of the treatment must be applied within a pre-defined fixed amount of of time.
#     '''
#     def __init__(self, name, id, processing_time, recovery time, treatment_sequence,
#                  num_shifts_to_complete_treatment = None, min_num_hours_btwn_treatments = None):
#         super().init(name,id, processing_time, recovery time)  
#         self.treatment_sequence = treatment_sequence
#         self.min_number_of_visits = len(treatment_sequence)
#         self.num_shifts_to_complete_treatment = num_shifts_to_complete_treatment # treatment must be completed
#         self.min_num_hours_btwn_treatments = min_num_hours_btwn_treatments

job_1 = Job("Widget1", "J234", "30-40", "20-10", 100, None)
job_2 = Job("Widget2", "J234", "30-40", "20-10", 100, None)

print(job_1.name, job_1.id, job_1.processing_time, job_1.recovery_time)

# print(issubclass(Job_with_Treatment, Job)) 
print(isinstance(job_1, Job))

print(job_1.group_p_r_times())

# print(job_1.__dict__)
# print(Job.num_unique_jobs)

print(Job.set_workday(27))
print(Job.num_hrs_per_workday)
print(job_1.num_hrs_per_workday)
print(job_1.num_hrs_per_shift)


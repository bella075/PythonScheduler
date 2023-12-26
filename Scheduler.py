import pandas as pd 
import yaml
from pathlib import Path  

# Job shop scheduler 
class Widget:
    num_unique_widgets = 0
    num_hrs_per_workday = 21
    num_shifts = 3
    num_hrs_per_shift = num_hrs_per_workday / num_shifts #assume equal shifts

    '''
    Each widget will have, at minimum:
    name -> string
    id -> string
    work_seq_str -> work sequence to manufacture a widget. A string of processing times and downtimes in minutes for a given work sequence.
        A work sequence can have one process or many processes. If there is more than one process in the seuqence, then
        processing times will be separated by a "-" delimiter. Processing time includes setup time, but does not include
        downtime. If idle time is required after process, p, then a "/" delimtier will follow the 
        processing time and the idle time,i, will be given. Idle time may be required if widget needs to cool or set before
        commencing the next step inthe work sequence.
            Example: 20-10/3-10/4. The second process takes 10 minutes and 3 minutes of idle time are required.
        The total time the widget consumes for the workstation will be the processing time + idle time 
    cost_dollars -> includes labor and material cost for a widget

    Some widgets may require special treatments. If a series of treatments are required, it is assummed that the
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
        try:
            self.treatment_sequence = treatment_sequence.split("-")
            if len(self.treatment_sequence) == 1:
                self.treatment_sequence = [0]
        except:
            self.treatment_sequence = [0]

        self.ls_proctime_idletime_tuples = Widget.combine_processing_and_idle_times(self)[0]
        self.ls_proctime_plus_idletime = Widget.combine_processing_and_idle_times(self)[1]
        self.min_num_widget_req_for_full_treatment = Widget.min_num_widget_req_for_full_treatment(self)

    num_unique_widgets += 1

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
    
    def min_num_widget_req_for_full_treatment(self):
        if (len(self.treatment_sequence) / len(self.ls_proctime_plus_idletime)) > 1:
            min_num_widget_req_for_full_treatment = int((len(self.reatment_sequence) / len(self.ls_proctime_plus_idletime)))
        else: 
            min_num_widget_req_for_full_treatment = 1
        return min_num_widget_req_for_full_treatment

    @staticmethod
    def min_to_sec(x):
        return float(x)*60
    
    def export_single_widget_schedule_as_csv(self):
        ls_toa, ls_process_time, ls_shift_counter, ls_widget_counter = [], [], [], []
        ls_day_counter, ls_cost_dollars, ls_treatment_sequence= [], [], []
        elapsed_time = 0
        shift_counter, day_counter, treatment_counter = 1, 1, 0
        print("treatment_sequence", self.treatment_sequence)
        for w in range(self.min_num_widget_req_for_full_treatment):
            for count, tup in enumerate(self.ls_proctime_idletime_tuples):
                if count == 0:
                    ls_process_time.append(tup[0])
                    ls_toa.append(0)
                else:
                    ls_process_time.append(tup[0])
                    ls_toa.append(elapsed_time)

                elapsed_time = elapsed_time + tup[0] + tup[1]
                ls_shift_counter.append(shift_counter)
                ls_day_counter.append(day_counter)
                ls_cost_dollars.append(self.cost_dollars)
                ls_widget_counter.append(w)

                if self.treatment_sequence == [0]:
                    ls_treatment_sequence.append(None)
                elif treatment_counter < len(self.treatment_sequence):
                    ls_treatment_sequence.append(self.treatment_sequence[treatment_counter])
                    treatment_counter +=1
                else:
                    treatment_counter = 0 #restart counter
                    ls_treatment_sequence.append(self.treatment_sequence[0])

        columns = ["toa_at_work_station", "process_time_sec", "widget_counter", "shift_counter", "day_counter", "cost_dollars", "treatment_sequence"]
        data = list(zip(ls_toa, ls_process_time, ls_shift_counter, ls_widget_counter, ls_day_counter, ls_cost_dollars, ls_treatment_sequence ))

        df_export= pd.DataFrame(columns=columns, data=data)
        path = r"C:\Users\bella\Desktop\export.csv" # %self.name
        print(path)
        # print(df_export)
        df_export.to_csv(path, index=False)

    
def loadYAML(YAML_path):
    with open(YAML_path) as stream:
        data = yaml.safe_load(stream)
    print(data.keys())
    data["num_hrs_per_workday"]
    print(data["num_shifts"])
    
    print(data["published"])
    df_w = pd.DataFrame.from_dict(data["widget"])
    df_w["num_hrs_per_workday"] = data["num_hrs_per_workday"]
    df_w["num_shifts"] = data["num_shifts"]
    df_w["published"] = data["published"]
  
    print(df_w)
    return df_w

if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.

    widget_1 = Widget("Widget1", "J234", "40-20/10-30/20-80-50", 100, "100-75-50-25")
    # widget_2 = Widget("Widget2", "J234", "30-40", 100, None)

    #print(widget_1.name, widget_1.id, widget_1.work_sequence)
   
    widget_1.export_single_widget_schedule_as_csv()
    # print(issubclass(Widget_with_Treatment, Widget)) 
    # print(isinstance(widget_1, Widget))

    # print(widget_1.combine_processing_and_idle_times())

    # print(widget_1.__dict__)
    # print(widget.num_unique_widgets)
    # print(Widget.set_workday(27))
    # print(Widget.num_hrs_per_workday)
    # print(widget_1.num_hrs_per_workday)
    # print(widget_1.num_hrs_per_shift)

    # YAML_path = r"C:\Users\bella\PythonScheduler\widget_config.yaml"
    # df_w = loadYAML(YAML_path)

    



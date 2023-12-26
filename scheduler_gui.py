from Scheduler import Widget
from Scheduler import loadYAML

YAML_path = r"C:\Users\bella\PythonScheduler\widget_config.yaml"

df_w = loadYAML(YAML_path)

#update dataframe
ls_proctime_idletime_tuples, ls_proctime_plus_idletime, ls_total_work_seq_time= [], [], []
for idx, row in df_w.iterrows():
    name = row["name"]
    name = Widget(
    row["name"],
    row["id"], 
    row["work_sequence"],
    row["cost_dollars"], 
    row["treatment_sequence"]
    )

    df_w["treatment_sequence"][idx] = name.treatment_sequence

    print(name.id)
    ls_total_work_seq_time.append(sum(name.ls_proctime_plus_idletime))
    ls_proctime_idletime_tuples.append(name.ls_proctime_idletime_tuples)
    ls_proctime_plus_idletime.append(name.ls_proctime_plus_idletime)

df_w["proctime_idletime_tuples"] = ls_proctime_idletime_tuples
df_w["proctime_plus_idletime"] = ls_proctime_plus_idletime
df_w["total_work_seq_time"] = ls_total_work_seq_time
print(df_w)
Widget.set_num_shifts = df_w["num_shifts"][0]
Widget.set_workday = df_w["num_hrs_per_workday"][0]
print("num shifts", Widget.set_num_shifts)
print("num shifts", Widget.set_workday)

df_w["max_num_widgets_per_shift"] = ((Widget.set_workday/Widget.set_num_shifts)*60) / df_w["total_work_seq_time"]

print(df_w)



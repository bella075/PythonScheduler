import pandas as pd 

class Appointment:

    def __init__(self, first, last, service_time, downtime, cost_dollars ):
        # self.type = "short"
        self.first = first # first name
        self.last = last  # last name
        self.service_time = service_time # time in minutes of appt
        self.downtime = downtime # time in minutes after appt required for doctor to reflect and document
        self.cost_dollars = cost_dollars
        

appt_1 = Appointment("John", "Doe", 30, 10, 100 )

print(appt_1.first, appt_1.last, appt_1.service_time)
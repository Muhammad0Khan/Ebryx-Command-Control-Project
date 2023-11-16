import psutil as PS

print ("look here ")
print ("_____")
print("cpu times: ",PS.cpu_times())
print("cpu percentages: " ,PS.cpu_times_percent(interval=None, percpu=True))
print("cpu frequency:" ,PS.cpu_freq())
print("stats: " ,PS.cpu_stats())
print ("loading: ", PS.getloadavg())
print ("cpu count: ", PS.cpu_count(logical=True))

print ("<_____>")
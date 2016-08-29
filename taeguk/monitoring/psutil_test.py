import psutil

print(psutil.cpu_count())
print(psutil.cpu_count(logical=False))
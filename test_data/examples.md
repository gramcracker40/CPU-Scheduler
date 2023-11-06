# examples of sim.py usage

# FCFS examples
### Small
python sim.py test_data/CPUS.dat --cpus 2 --ios 2 --sched="FCFS" --speed=0.1
python sim.py test_data/IOS.dat --cpus 2 --ios 2 --sched="FCFS" --speed=0.1
### Medium
python sim.py test_data/CPUM.dat --cpus 8 --ios 10 --sched="FCFS" --speed=0.0001
python sim.py test_data/IOM.dat --cpus 8 --ios 10 --sched="FCFS" --speed=0.0001
### Large
python sim.py test_data/CPUL.dat --cpus 20 --ios 20 --sched="FCFS" --speed=0.0001
python sim.py test_data/IOL.dat --cpus 20 --ios 20 --sched="FCFS" --speed=0.0001

# Round Robin examples
### Small
python sim.py test_data/CPUS.dat --cpus 2 --ios 2 --sched="RR" --speed=0. --time_slice 5
python sim.py test_data/IOS.dat --cpus 2 --ios 2 --sched="RR" --speed=0.1 --time_slice 5
### Medium
python sim.py test_data/CPUM.dat --cpus 8 --ios 10 --sched="RR" --speed=0.0001 --time_slice 10
python sim.py test_data/IOM.dat --cpus 8 --ios 10 --sched="RR" --speed=0.0001 --time_slice 10
### Large
python sim.py test_data/CPUL.dat --cpus 20 --ios 20 --sched="RR" --speed=0.0001 --time_slice 15
python sim.py test_data/IOL.dat --cpus 20 --ios 20 --sched="RR" --speed=0.0001 --time_slice 15

# Priority based examples
python sim.py test_data/PrioSpreadXS.dat --cpus 1 --ios 1 --sched="PB" --speed=0.75
python sim.py test_data/PrioSpreadL.dat --cpus 24 --ios 30 --sched="PB" --speed=0.0001
python sim.py test_data/PrioSpreadS.dat --cpus 2 --ios 2 --sched="PB" --speed=0.0001
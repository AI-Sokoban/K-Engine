python newSokoban.py -m bfs -l level1.txt
@echo off
for /l %%n in (1, 1, 8) do (
 echo "level%%n.txt"
 python newSokoban.py -m astar -l level%%n.txt
 python newSokoban.py -m idastar -l level%%n.txt
)
pause
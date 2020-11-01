
timeout 2m python3 tunneler.py --grid $1 --phase $2 --tunnel $3

python3 game.py --grid $1 --phase $2 --tunnel $3
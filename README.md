# SIRS Model of Conway's Game of Life

## Motivation

To create a mathematical model of a susceptible->infected->recovered->susceptible (SIRS) disease system

## Components

 - Susceptible People (S)
   - Default state
   - Every turn, if touching an infected individual, roll to see if S becomes infected
   - After recovering, people become susceptible again over time
   
 - Infected People (I)
   - Every turn, roll to see if I dies
   - Every turn, roll to see if I recovers
   
 - Recovered People (R)
   - People that recover from infection
   - By default, recovered people have eight (8) turns of immunuty
   - immunity is reduced by two (2) turns per adjacent infected individual
   
 - Dead People (D)
   - No longer part of the population
   - Cannot be infected
   - Cannot recover
   
## Command Line

Run in PowerShell, Command Prompt, or Terminal: `python ./SIRS_Game_of_Life.py`

 - Default `timeframe`: 30
 - Default `initial_infect`: 1
 - Default `initial_immunity`: 0
 - Default `infect_probability`: 17
 - Default `death_probability`: 0
 - Default `recovery_probability`: 0
 - Default `world_dimensions`: 64
 
## Arguments

 - timeframe (-t): number of intervals to run the simulation (positive integer 1 - inf)
 - initial_infect (-i0): initial percent of population infected (integer 0 - 100)
 - initial_immunity (-r0): initial percent of population immune (integer 0 - 100)
 - infect_probability (-I): percent chance of infection (integer 0 - 100)
 - death_probability (-D): percent chance of death (integer 0 - 100)
 - recovery_probability (-R): percent chance of recovery (integer 0 - 100)
 - recovery_length (-r): Turns spent immune after recovery (integer 0 - inf)
 - world dimensions (-W): width/height of the world (integer 1 - inf)

## Flags
 - Save Latest Run (--SAVE): Saves every time-step of the simulation into the "./Latest_Run" directory
 - Show Graph (--GRAPH): Displays the graph of Susceptible/Infected/Recovered/Deceased vs Time at the end of the simulation
 - Command Line Only (--NOGUI): Only use command line arguments and skip displaying the GUI
 

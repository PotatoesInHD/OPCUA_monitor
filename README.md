## OPCUA FILE MONITOR - WIP still needs more testing.

### What does it do?
- This python program connects to a PLC by OPCUA and monitors a files modified time stamps for changes.  
  - I made this with monitoring .MDB files in mind but it can monitor any files timestamps in STATIC_FILE_MODE. 
- If a change is detected it writes to an OPCUA node that the PLC can monitor.
- File its monitoring changes name every new day with the date as its name.  So program creates the new file name to monitor each day.
  - using this format "9-15-2026-BS.mdb".  Static file mode and file name can be configured in config.ini.
- It also writes a heart beat signal to an OPCUA node so the PLC knows when communication is lost.
- It will run on windows/linux and as a script or as an exe.  It handles windows/linux and script/exe pathing differences on its own. 
- If there is a disconnection such as a network cable unplugged or PLC power cycle the monitoring program will continue to attempt reconnecting.
- It will display connection status to the GUI.
- It will handle and log all errors to the log files.
<br><br>
## It's Log it's Log it's better than bad it's good!

There are three separate logging files 
- Log for timestamps of when the monitored file was modified
  <img width="1002" height="25" alt="Image" src="https://github.com/user-attachments/assets/c2e1d89e-6854-4853-9109-771a66e014a6" />
- Log for Warnings/Errors
  <img width="1104" height="46" alt="Image" src="https://github.com/user-attachments/assets/eebf4dd4-cab5-4a50-859b-996930d26034" />
- Log for OPCUA communication info/traffic shenanigans.  This one can be disabled via the Config.ini file "ENABLE_OPCUA_INFO_LOGS"
  <img width="1172" height="46" alt="Image" src="https://github.com/user-attachments/assets/67ba7a30-8515-42f4-ad70-6a3e31a4e7e0" />

These log files are created automatically in a logs folder where the script or .exe lives, if made into .exe using pyinstaller.
Once a log reaches 10MB it will create another "log.1" and keep rotating.  So 20MB and 2 files each per log type
<br><br>
## Config.ini
Config.ini file must be in same folder as opcua_mon.py/exe !<br>
This is utilized so settings can be changed easily even after bundling with pyinstaller.<br>
Limits in the config.ini are hard coded into config.py file to help prevent any fat finger issues. 

**\# -----------------------ConfigFile-------------------------------------<br>**
\# config.ini file must stay in same directory as opcua_mon.exe

**\# -----------------------OPCUA SETUP-------------------------------<br>**
**[OPCUA_NODE]**<br>
*\# Example: ns=1;i=2000<br>*
TO_PLC_HEARTBEAT_NODE = ns=1;i=2000<br>
TO_PLC_FILE_WRITE_DETECTED_NODE = ns=1;i=2002<br>
OPCUA_SERVER_STATE = ns=0;i=2259<br>
*\# Example: opc.tcp://192.168.2.199:4840<br>*
OPCUA_URL = opc.tcp://IPADDRESS:4840<br>

**[OPCUA_CONFIG]<br>**
*\# Limited from 20_000-60_000ms<br>*
SESSION_TIMEOUT = 30_000<br>

*\# Default 4 but causes not responding on gui so made 2s<br>
\# Limited from 1.0-4.0s<br>*
SOCKET_TIMEOUT = 2<br>

*\# If server status check fails it initiates reconnect sequence<br>
\# Limited from 2.0-10.0s<br>*
CHECK_SERVER_STATUS_INTERVAL = 5.0<br>

*\# Heart beat signal to PLC<br>
\# Limited from 1.0-5.0s<br>*
HEART_BEAT_INTERVAL = 3.0<br>

*\# Limited from 0.2-2.0s<br>*
DELAY_BETWEEN_WRITES = 0.2<br>

*\# Prevents looping faster than necessary<br>*
*\# Limited from 0.2-2.0s<br>*
MAIN_LOOP_DELAY = 0.2<br>

**\# -------------------------FILE SETUP-----------------------------------<br>**
**[MDB_DIR_PATH]<br>**
\# Path to .MDB files, where servopress data is stored.<br>
\# Example: C:\Users\user\desktop\servodaata<br>
MDB_DIR_PATH = .<br>

**[LOG_CONFIG]<br>**
*\# Enable or disable OPCUA_info_logs<br>*
*\# True or False<br>*
ENABLE_OPCUA_INFO_LOGS = True<br>

**\# ------------------------TESTING ONLY-----------------------------------<br>**
*\# Test file must be in same directory as opcua_mon<br>*
**[TEST]<br>**
*\# Example: test_file.txt<br>*
TEST_FILE = test_file.txt<br>
*\# True or False<br>*
TEST_MODE = True<br>
<br><br>
## GUI
There is a simple GUI made with tkinter that will display "Connecting..."" in red or "Connected!"" in green.<br>
This status is based on the OPCUA server connection status.  The monitor program checks the server status node on<br>
a defined interval from "CHECK_SERVER_STATUS_INTERVAL" in the config.ini.

<img width="789" height="485" alt="Image" src="https://github.com/user-attachments/assets/051dcf4e-03d3-4ae6-b2e5-9ea77c7a30c3" />

The GUI was a bit of an afterthought.  I already have a background thread for running the heart beat pulse and<br>
didn't want to refactor everything else onto another background thread so that tkinter could run its own mainloop().
So the GUI willsometimes hang for 1-2 seconds if the PLC is trying to connect/reconnect because it is busy working its magic.
The SOCKET_TIMEOUT value in the config.ini is set to 2 seconds to help with this issue.  time.sleep() instructions were also
avoided to prevent GUI "not responding". In their place I added a sleep_helper() function that that will constantly call window.update() as it runs.<br>

In the future I might refactor the threading for the tkinter GUI to run better or maybe just go to a CLI interface since its not displaying anything fancy.<br>

**Once connected though, the GUI is smooth as eggs.**<br><br>

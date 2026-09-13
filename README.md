bootdev solo project.  

creating a python program to monitor .MDB file. Either through modified timestamps or by monitoring contents of MDB file.  Still working out the details.

If MDB file is updated python will send signal to PLC using OPCUA. 
This is to let PLC know press data is being stored properly in MDB file to prevent missing data.  If MDB file doesn't get updated then we can send signal to PLC telling it to stop process.

will sweeten this read me at some point maybe

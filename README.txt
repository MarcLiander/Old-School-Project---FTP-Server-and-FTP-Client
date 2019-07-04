Name: Marc Liander Camacho Reyes
E-mail: MarcLianderReyes@gmail.com

I worked on my own for this assignment.


Programming Language: Python 3


How to execute programs:

-For client.py:
Windows - "py client.py <server_name> <server_port [integer]>"
Linux - "python3 client.py <server_name> <server_port [integer]>"

-For server.py:
Windows - "py server.py <server_port [integer]>"
Linux - "python3 server.py <server_port [integer]>"

The commands must be done in the console and in the directory of the appropriate files. The server_port integers must be matching for the control connection to establish.

Notes:
-The files were successfully tested in the following environemnts:
	-Windows 8.1
	-Windows 10
	`Ubuntu
-Successful testing was done through both localhost (same computer) and two different computers on the same network (LAN)
-Failed testing occurred when trying to use a virtual machine to connect to another computer on the same network 
	-observed problem (virtual machine = client.py, other computer = server.py): IP Address being obtained by server (other computer) was that of the, host machine, rather than the IP Address of the virtual machine 
-The following file types were used in the test (and all were perfectly copied in the transfers):
	-.png
	-.pdf
	-.docx
	-.txt
	-.mp4
	-.mkv
	-.py
	-.mp3
	-.lip
	-<no file type listed after>
-Largest file size that was successful 100% of the time was: 136,026 kb
-Largest file size that was successful sometimes: 333,880 kb
	-Observed problem: forced termination from the client's computer
	-Theorized cause: MemoryError due to the capabilities of the computers being used for testing
-Largest file size attempted that did not work at all: 559,128 kb
-Uncertain if same file sizes will be successful/failures on other machines, due to differing capabilities of other machines
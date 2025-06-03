RDJD's Task Manager

A lightweight Windows Task Manager built with Python and Tkinter, offering real-time process monitoring, GUI task handling, and system performance metrics.

Features:

Processes Tab:

  View all running processes with PID, name, and memory usage.
  
  Search and filter processes.
  
  Terminate selected processes.
  
Tasks Tab:

  Shows active GUI applications.
  
  Launch new tasks via file explorer.
  
  End GUI tasks safely.
  
Performance Tab:

  View live CPU, RAM, and Disk usage.
  
Auto-Refresh:

  Background thread updates all tabs every 5 seconds.

![Screenshot 2025-06-03 191700](https://github.com/user-attachments/assets/0f13a762-a834-4365-b639-e629aee73bae)
![Screenshot 2025-06-03 191810](https://github.com/user-attachments/assets/64d56024-19d8-4baf-8e26-0900a8d3e301)
![Screenshot 2025-06-03 191902](https://github.com/user-attachments/assets/ad5ed17f-db1d-4374-9ba2-a4a5443f2cb8)
![Screenshot 2025-06-03 192025](https://github.com/user-attachments/assets/eb74d8c9-59f2-4625-b050-888abadee8e5)

Prerequisites:
Python 3.9 or higher
Works on Windows only (due to os.startfile() and pywinctl dependencies)

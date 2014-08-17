My Task
=======

MyTask is a simple task managment tool.

Features
--------
  - Creating simple taks - 
                         - task add "task description" (%YYYY-%MM-%DD:%HH:%MM|today|tomorrow) (DAILY|WEEKLY|NONE)
                         - Items in () are optional
  - Delete task - 
                - task delete <task_id>
  - list tasks   - 
                - task short (short description of tasks)
                - task long (you guessed it)
  - task deletion - 
                  - task delete <task_id>
  - supports conky color themes
  - task agenda - This will print the agenda for the week - 
                - task agenda
                - task agenda -type (conky|bash)
  - Desktop notifications via notify-send - 
                - task notify (may be you want to put this in a cron job)
  - Task snooze - 
                - task snooze <taskid> <time>

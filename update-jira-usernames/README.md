# Update username for all Jira Users
This script updates all users from **jira-software-users** group using Jira REST API.

# Setup
* Create separate Python Virtual environment. You can refer to [Real Python PyEnv Introduction](https://realpython.com/intro-to-pyenv/) to get started.
* pip install -r requirements.txt
* Rename sample.env file as .env and update parameters to correct values.
* To run script
~~~
python update-jira-usernames.py
~~~
* Script will create following files:
  * jira-software-users.<jira_env>.txt - Jira Users Information backup!
  * script-execution.log

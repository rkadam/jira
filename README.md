# All about Jira
It's quite fun to interact with [Jira](https://atlassian.com/software/jira) and use available APIs to automate mundane Adminstration tasks to make life easy! I also enjoy tinkering with [ScriptRunner](https://www.adaptavist.com/atlassian-apps/scriptrunner-for-jira/) which is best thing happen to Jira platform IMHO. 

This Repository is going to host all Jira related scripts in one place.

## Environment
* Python
* Jupyter Notebook
* Postman

## Libraries
* [python-dotenv](https://pypi.org/project/python-dotenv/) - Greatly helps in managing credentials from .env
* [Tqdm](https://github.com/tqdm/tqdm) - Progress Bar for Python CLI applications
* [Python Requests](https://requests.readthedocs.io/en/master/) - Must use library to interact with Web Applications using Python
You should use **requirements.txt** to load all these libraries!

### Helper Scripts
* I've included Jupyter Notebook **jira-user-groups-helper** which has following methods to help in group and user management in Jira.
  * Method **create_users** create new user in Jira. Input CSV file.
  * Method **add_users_to_group** add listed users into given jira group.
  * Method **remove_users_from_group** removes listed users from given jira group.
  * Method **get_users** gets list of users for given jira group.
  * Method **update_jira_username** updates username for given user with new username.
  * Method **process_jira_username_updates** calls method _update_jira_username_ internally; also takes backup of list of users before updating usernames.

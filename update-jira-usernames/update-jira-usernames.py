import logging
import requests
from dotenv import load_dotenv
import os
import sys
from pprint import pformat
import json
from datetime import datetime

# https://towardsdatascience.com/progress-bars-in-python-4b44e8a4c482?gi=6a0158a5a16e
from tqdm.auto import tqdm

logging_level_dict = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'CRITICAL': logging.CRITICAL
}

def get_jira_users(jira_logger, jira_base_url, auth, group_name, include_inactive_users, start_at):

    users = []
    user_count = 0
    pbar = tqdm(total=100)

    resp = requests.get(f'{jira_base_url}rest/api/2/group/member?groupname={group_name}&includeInactiveUsers={include_inactive_users}&startAt={start_at}', auth=auth)    
    if resp.status_code == 200:
        total = resp.json()['total']
        start_at = resp.json()['startAt']
        current_result_count = len(resp.json()['values'])

        while (current_result_count > 0):
            jira_logger.debug(f'Total - {total}, Starts At - {start_at}, Current Result Count - {current_result_count}')
            current_user_set = resp.json()['values']
            for i in range(current_result_count):
                jira_logger.debug(f"{current_user_set[i]['name']},{current_user_set[i]['emailAddress']},{current_user_set[i]['displayName']},{current_user_set[i]['active']}")
                users.append(f"{current_user_set[i]['name']},{current_user_set[i]['emailAddress']},{current_user_set[i]['displayName']},{current_user_set[i]['active']}")
                user_count += 1
            
            percent = (current_result_count/total)*100
            pbar.update(percent)

            # Get next set of results if available.
            start_at = start_at + current_result_count            
            resp = requests.get(f'{jira_base_url}rest/api/2/group/member?groupname={group_name}&includeInactiveUsers={include_inactive_users}&startAt={start_at}', auth=auth)    
            current_result_count = len(resp.json()['values'])
    else:
        jira_logger.error(f"Response Code: {resp.status_code}, Response Message: {resp.text}")

    jira_logger.info(f"Total {user_count} users found in group - '{group_name}'")    
    pbar.close()

    return users

def update_jira_username(jira_logger, jira_base_url, auth, username, new_username_value):

    is_update_successful = True
    update_status_code = 200
    update_status_message = ""
    
    headers = {'Content-type': 'application/json'}
    
    # name is username attribute in Jira Internal Directory
    json_body = {
        'name' : new_username_value
    }
    
    resp = requests.put(f'{jira_base_url}rest/api/2/user?username={username}', data=json.dumps(json_body), auth=auth, headers=headers)
    if resp.status_code != 200:
        is_update_successful = False
        update_status_code = resp.status_code
        update_status_message = resp.json()["errors"]["active"]
        jira_logger.error(f"Response Code: {update_status_code}, Response Message: {update_status_message}")
    
    jira_logger.info(f"{username} - update status: {is_update_successful}")
    return is_update_successful, update_status_code, update_status_message

# update user name with value from emailAddress
def update_jira_usernames(jira_logger, jira_base_url, auth, group_name, user_dict):
    update_operation_status_list = []
    update_operation_status_list.append("username,Is Update Successful?, Error Details")

    with open(f"{group_name}.group_users_update_execution.csv", "a") as output_csvfile:

        output_csvfile.writelines("\n\n")
        output_csvfile.writelines(datetime.now().strftime("%d/%b/%Y %H:%M:%S") + "\n\n")
        
        for username in user_dict:
            #if username is already updated to email, skip this user!
            if username != user_dict[username]:
                jira_logger.info(f"Update username from {username} to {user_dict[username]}")
                update_status_info_tuple = update_jira_username(jira_logger, jira_base_url, auth, username, user_dict[username])
                jira_logger.debug(f"{username} - {update_status_info_tuple[0]}")
                update_operation_status_list.append(username + "," + str(update_status_info_tuple[0]) + "," + update_status_info_tuple[2])
                output_csvfile.writelines(username + "," + str(update_status_info_tuple[0]) + "," + update_status_info_tuple[2]+ "\n")
            
def main():

    load_dotenv(override=True)

    jira_base_url = os.getenv('JIRA_ENV_BASE_URL')
    jira_env = os.getenv('JIRA_ENV')

    jira_logger = logging.getLogger(__name__)
    # Following check is necessary otherwise everytime we run this in Jupyter lab Cell, new handler is getting added resulting in duplicate logs printed!
    if not jira_logger.handlers:
        jira_logger.setLevel(logging_level_dict[os.getenv('LOG_LEVEL')])

        file_handler = logging.FileHandler(os.getenv('LOG_FILE'))
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - line %(lineno)d - %(message)s'))

        out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(logging.Formatter('line %(lineno)d - %(message)s'))

        jira_logger.addHandler(out_hdlr)
        jira_logger.addHandler(file_handler)

    auth = (os.getenv('USERID'), os.getenv('PASSWORD'))

    group_name = 'jira-software-users'
    include_inactive_users = 'true'
    start_at = 0
    
    jira_logger.info("Reteriving current usernames to store in backup file!")
    users = get_jira_users(jira_logger, jira_base_url, auth, group_name, include_inactive_users, start_at)
    
    if users:
        jira_logger.info("Backup complete!")
        # First write current usernames into backup file in case we need them.
        with open(f"{group_name}.{jira_env}.txt", 'w') as filehandle:
            filehandle.writelines("username,email,display_name,is_user_active\n")
            filehandle.writelines("%s\n" % user for user in users)

        username_email_dict = {}
        for user in users:
            #Also we will skip username as which we will be running this script, so that subsequent calls will not fail!
            username = user.split(',')[0].strip()
            email = user.split(',')[1].strip()
            # We don't want to update logged in User's username otherwise script will fail.
            # we will need to update username to email to make it working agian!
            if username not in [os.getenv('USERID')]:
                username_email_dict[username] = email

        jira_logger.info("Updting usernames now...")
        update_jira_usernames(jira_logger, jira_base_url, auth, group_name, username_email_dict)
        jira_logger.info("Update complete!")

if __name__ == '__main__':
    main()

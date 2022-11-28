#!/usr/bin/env python3

import os
import shutil
import logging
from datetime import datetime
from git import Repo

# Envermoment variables values #
logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] (%(name)s) %(process)d-%(threadName)s ---> %(message)s'
        )
logging.info("Set envermoment variables values")

CP_DIRS_LIST = [
    '/opt/airflow/dags',
    '/opt/airflow/dag_configs',
    '/opt/airflow/ibe_model_bcp',
    '/opt/airflow/python_home',
    '/opt/airflow/qa'
]

DIR_REPLACE = "/opt/airflow"
GIT_DST_DIR = "/opt/gyt_sync_script/dag_airflow"
GIT_BRANCH = "dev"
GIT_REPO = r'/opt/gyt_sync_script/dag_airflow/.git'
GIT_ACCESS_TOKEN = "***"
GIT_COMMIT_MESSAGE = "empty"

logging.info(
            f"\nCP_DIRS_LIST: {CP_DIRS_LIST}"
            f"\nDIR_REPLACE: {DIR_REPLACE}"
            f"\nGIT_DST_DIR: {GIT_DST_DIR}"
            f"\nGIT_BRANCH: {GIT_BRANCH}"
            f"\nGIT_REPO: {GIT_REPO}"
            f"\nCOMMIT_MESSAGE: {GIT_COMMIT_MESSAGE}"
        )
# Envermoment variables values #


# Def from list and copy files to gitlab repository #
def cp_src_to_dst(SRC_DIR):
    logging.info("cp_src_to_dst(SRC_DIR): start def with args: " + SRC_DIR)
    for src_dir, dirs, files in os.walk(SRC_DIR):
        dst_dir = src_dir.replace(DIR_REPLACE, GIT_DST_DIR, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                if os.path.samefile(src_file, dst_file):
                    continue
                os.remove(dst_file)
            shutil.copy2(src_file, dst_dir)
    logging.info("cp_src_to_dst(SRC_DIR): finish def with args: " + SRC_DIR)
# Def from list and copy files to gitlab repository #


# Def generate commit message body from gitlab repository push operations #
def gen_commit_message():
    now = datetime.now()
    TIMESTAMP = now.strftime("%d/%m/%Y %H:%M:%S")
    BODY_COMMIT_MESSAGE = str(TIMESTAMP) + ": host: host-1, dags updated with a py script in the cron"
    return BODY_COMMIT_MESSAGE
# Def generate commit message body from gitlab repository push operations #


# Def from git push content #
def git_push():
    logging.info("git_push(): start def")
    try:
        logging.info("git_push(): git.Repo.init")
        repo = Repo.init(GIT_REPO)
        logging.info("git_push(): start git pull")
        repo.git.pull('origin', GIT_BRANCH)
        logging.info("git_push(): start git add")
        repo.git.add(update=True)
        logging.info("git_push(): gen_commit_message(): generate commit message body")
        GIT_COMMIT_MESSAGE = gen_commit_message()
        logging.info("git_push(): start git commit")
        repo.index.commit(GIT_COMMIT_MESSAGE)
        logging.info("git_push(): start git push")
        repo.git.push('origin', GIT_BRANCH)
    except Exception as e:
        logging.info("git_push(): error exception: " + str(e))
# Def from git push content #


def main():
    logging.info("main(): start recursive list files in " + str(CP_DIRS_LIST))
    for DIR in CP_DIRS_LIST:
        cp_src_to_dst(DIR)
    git_push()


if __name__ == "__main__":
    logging.info("Init main():")
    main()

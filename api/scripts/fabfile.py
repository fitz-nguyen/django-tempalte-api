from fabric.api import cd, env, hosts, local, run, sudo
from fabric.contrib.files import exists

SITE_FOLDER = "~/app"
REPO_URL = ""

env.roledefs = {
    "dev": {"hosts": ["host"], "code_dir": SITE_FOLDER, "code_branch": "develop"},
    "prod": {
        "hosts": ["host1", "host2"],
        "code_dir": SITE_FOLDER,
        "code_branch": "master",
    },
}

env.user = "ubuntu"
env.key_filename = ""


def deploy():
    """
    :return:
    """
    with cd(SITE_FOLDER):
        _pull_develop_code()
        _update_virtualenv()
        _update_database()
        _restart_django()
        _update_static_files()


def _get_latest_source():
    if exists(".git"):
        run("git fetch")
    else:
        run("git clone {REPO_URL} .")
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run("git reset --hard {}".format(current_commit))


def _update_virtualenv():
    run(f"{SITE_FOLDER}/virtualenv/bin/pip install -r requirements/local.txt")


def _update_database():
    run(f"{SITE_FOLDER}/virtualenv/bin/python manage.py migrate --noinput")


def _update_static_files():
    run(f"{SITE_FOLDER}/virtualenv/bin/python manage.py collectstatic --noinput")


def _pull_develop_code():
    run("git checkout develop")
    run("git pull --rebase origin develop")


def _pull_master_code():
    run("git checkout master")
    run("git pull --rebase origin master")


def _restart_django():
    sudo("systemctl restart supervisor")

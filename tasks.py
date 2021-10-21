import os
import shutil
from invoke import task, run

with open('tox.ini') as fp:
    lines = fp.read().split("\n")
    dockers = [line.split("=")[1].strip() for line in lines
               if line.find("name") != -1]


@task
def devenv(c):
    """Builds a development environment: downloads, and starts all dockers
    specified in the tox.ini file.
    """
    clean(c)
    cmd = 'tox -e devenv'
    for d in dockers:
        cmd += " --docker-dont-stop={}".format(d)
    print("Running: {}".format(cmd))
    run(cmd)

@task
def clean(c):
    """Stop all dockers, and clean up the built binaries, if generated."""
    if os.path.isdir("build"):
        shutil.rmtree("build")
    if os.path.isdir("dist"):
        shutil.rmtree("dist")
    run("docker rm -f {}".format(' '.join(dockers)))

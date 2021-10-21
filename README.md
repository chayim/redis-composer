# composer

This is a tool to make it reasonably painless to generate docker-compose and environment files that can be sourced by a test case. The current assumption is that things are based on redis dockers. Composer looks for available ports on your computer, and then randomly assigns those to the mapped docker ports.

To use, create a configuration like the [sample configuration file](sample-config.yml).  Each *environment* is a series of docker containers to create, within the docker-compose file.  Images are created based on those listed, and the number of images created.   As per the sample configuration file, the *redis-standalone* environment will create 5 redis instances, and 2 redisjson instances.

See the *docker-compose.yml* and *env* files that will be generated, as output examples.

---------

### Requirements

**Requirements**

* Python > 3.6
* pip > 20.0.3
* poetry > 1.10

**Setting up your development environment**

Once you have a virtualenv:

```poetry install```

### Running composer

```
python runner.py -h

Options:
  -h, --help            show this help message and exit
  -s FILE, --srcfile=FILE
                        Path to environment rules file.
  -d DIR, --dest=DIR    Directory in which to generate files
  -e <class 'str'>, --environment=<class 'str'>
                        Environment to generate
  -l, --listenvs        If set, list the available environments and exit.
  -P PORT_START, --port_start=PORT_START
                        Start finding free ports above this number.
  -E PORT_END, --port_end=PORT_END
                        Stop finding free ports below this number.
```

----

# tox dockers

For now, there's a placeholder tox file, to run multiple docker instances. Eventually this becomes a tool, but it's to get over the hump.

```
invoke -l

invoke devenv
```

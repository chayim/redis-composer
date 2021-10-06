import socket
import jinja2
from optparse import OptionParser
import sys
import os
import yaml
import random

def scan(start_port=7000, end_port=50000, host='localhost'):
    """Return the available ports for the target host."""
    ports = []
    for port in range(start_port, end_port):
        socket.setdefaulttimeout(0.3)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            res = s.connect((host, port))
        except socket.error:
            ports.append(port)
            continue
        s.close()

    return ports

def parse(srcfile):
    with open(srcfile) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    # TODO validate with yamale
    return cfg

def generate(yamlstruct, destdir, envname, ports):
    if not os.path.exists(destdir):
        os.makedirs(destdir)

    conf = yamlstruct['environments'][envname]
    num_ports = sum([list(val.values())[0] for val in conf['images']])
    our_ports = [random.randint(ports[0], ports[-1]) for i in range(0, num_ports+1)]

    context = {'ports': ports, 
               'conf': conf,
               'environment': envname,
               'dockers': [],
    }
    h = os.path.dirname(os.path.abspath(__file__))
    tl = jinja2.FileSystemLoader(h)
    env = jinja2.Environment(loader=tl)
    tmpl = tl.load(name='composer.tmpl', environment=env)


    portmap = []
    c = 0
    for img in conf['images']:
        image = list(img.keys())[0]
        num_images = list(img.values())[0]
        for n in range(0, num_images+1):
            port = our_ports[c + n]
            name = "{}_{}_{}".format(envname.replace('-', '_'), 
                                     image.split('/')[1], 
                                     n)
            d = {'image': image, 'name': name, 'port': port}
            # prepare the context for the docker-compose template
            context['dockers'].append(d)

            # just add the string for the env file
            portmap.append("{}={}".format(name, port))
        c += 1

    destplate = os.path.join(destdir, "docker-compose.yml")
    with open(destplate, "w+") as f:
        f.write(tmpl.render(context))
    sys.stdout.write("Docker template written to {}.\n".format(destplate))

    envfile = os.path.join(destdir, "env")
    with open(envfile, "w+") as fp:
        for p in portmap:
            fp.write("{}\n".format(p))
    sys.stdout.write("Env map written to {}\n".format(envfile))

if __name__ == "__main__":

    p = OptionParser(usage="-h")
    p.add_option("-s", "--srcfile", metavar="FILE", dest="SRCFILE",
                 help="Path to environment rules file.")
    p.add_option("-d", "--dest", metavar="DIR", dest="DESTDIR",
                 default=os.getcwd(),
                 help="Directory in which to generate files")
    p.add_option("-e", "--environment", metavar=str, dest="ENV",
                 help="Environment to generate")
    p.add_option("-l", "--listenvs", action="store_true", default=False,
                 dest="LISTENVS",
                 help="If set, list the available environments and exit.")

    p.add_option("-P", "--port_start", type=int, default=5000,
                 dest="PORT_START",
                 help="Start finding free ports above this number.")
    p.add_option("-E", "--port_end", type=int, default=6000,
                 dest="PORT_END",
                 help="Stop finding free ports below this number."),

    opts, args = p.parse_args()

    if opts.SRCFILE is None:
        sys.stderr.write("Please specify a source rules file.\n")
        sys.exit(3)

    if os.path.isfile(opts.SRCFILE) is False:
        sys.stderr.write("{} does not exist.\n".format(opts.SRCFILE))
        sys.exit(3)

    if 65535 > opts.PORT_START < 0:
        sys.stderr.write("Invalid start port.\n")
        sys.exit(3)

    if 65535 > opts.PORT_END < 0:
        sys.stderr.write("Invalid end port.\n")
        sys.exit(3)

    parsed = parse(opts.SRCFILE)
    environments = parsed['environments']
    if opts.LISTENVS:
        sys.stderr.write("Available environments are: \n\n")
        for e in environments:
            sys.stdout.write("{}\n".format(e))
        sys.exit(0)

    if opts.ENV not in environments:
        sys.stderr.write("Invalid environment. The available environments are: \n\n")
        for e in environments:
            sys.stdout.write("{}\n".format(e))
        sys.exit(3)

    conf = parse(opts.SRCFILE)
    ports = scan(opts.PORT_START, opts.PORT_END)
    generate(conf, opts.DESTDIR, opts.ENV, ports)
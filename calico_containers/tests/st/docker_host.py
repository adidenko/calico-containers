import sh
from sh import docker

from utils import get_ip, delete_container


class DockerHost(object):
    """
    A host container which will hold workload containers to be networked by calico.
    """
    def __init__(self, name):
        """
        Create a container using an image made for docker-in-docker. Load saved images into it.
        """
        self.name = name

        pwd = sh.pwd().stdout.rstrip()
        docker.run("--privileged", "-v", pwd+":/code", "--name", self.name, "-tid", "jpetazzo/dind")

        self.ip = docker.inspect("--format", "{{ .NetworkSettings.IPAddress }}",
                                 self.name).stdout.rstrip()
        self.execute("while ! docker ps; do sleep 1; done && "
                     "docker load --input /code/calico_containers/calico-node.tar && "
                     "docker load --input /code/calico_containers/busybox.tar && "
                     "docker load --input /code/calico_containers/nsenter.tar")

    def execute(self, command, use_powerstrip=False, **kwargs):
        """
        Pass a command into a host container. Appends some environment
        variables and then calls out to DockerHost._listen. This uses stdin via
        'bash -s' which is more forgiving of bash syntax than 'bash -c'.

        :param use_powerstrip: When true this sets the DOCKER_HOST env var. This
        routes through Powerstrip, so that Calico can be informed of the changes.
        """
        etcd_auth = "export ETCD_AUTHORITY=%s:2379;" % get_ip()
        stdin = ' '.join([etcd_auth, command])

        if use_powerstrip:
            docker_host = "export DOCKER_HOST=localhost:2377;"
            stdin = ' '.join([docker_host, stdin])
        return self._listen(stdin, **kwargs)

    def _listen(self, stdin, **kwargs):
        """
        Feed a raw command to a container via stdin.
        """
        return docker("exec", "--interactive", self.name,
                      "bash", s=True, _in=stdin, **kwargs)

    def delete(self):
        """
        Have a container delete itself.
        """
        delete_container(self.name)
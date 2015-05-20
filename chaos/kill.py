import logging
from subprocess import CalledProcessError

from chaos_monkey_base import (
    Chaos,
    ChaosMonkeyBase,
)
from utility import (
    NotFound,
    run_shell_command,
)

__metaclass__ = type


class Kill(ChaosMonkeyBase):
    """Kills a process or shutdown a unit"""

    def __init__(self):
        self.group = 'kill'
        super(Kill, self).__init__()

    @classmethod
    def factory(cls):
        return cls()

    def get_pids(self, process):
        pids = run_shell_command('pidof ' + process, quiet_mode=True)
        if not pids:
            return None
        return pids.strip().split(' ')

    def kill_jujud(self, quiet_mode=True):
        pids = self.get_pids('jujud')
        if not pids:
            logging.error("Jujud process ID not found")
            if not quiet_mode:
                raise NotFound('Process id not found')
            return
        run_shell_command('kill -s SIGKILL ' + pids[0])

    def kill_mongodb(self, quiet_mode=True):
        pids = self.get_pids('mongod')
        if not pids:
            logging.error("MongoDB process ID not found")
            if not quiet_mode:
                raise NotFound('Process id not found')
            return
        run_shell_command('kill -s SIGKILL ' + pids[0])

    def restart_unit(self, quiet_mode=False):
        try:
            run_shell_command('shutdown -r now')
        except CalledProcessError:
            logging.error("Error while executing command: shutdown -r now ")
            if not quiet_mode:
                raise

    def get_chaos(self):
        chaos = list()
        chaos.append(
            Chaos(
                enable=self.kill_jujud,
                disable=None,
                group=self.group,
                command_str='jujud',
                description='Jujud process has been killed.'))
        chaos.append(
            Chaos(
                enable=self.kill_mongodb,
                disable=None,
                group=self.group,
                command_str='mongod',
                description='Mongod process has been killed.'))
        return chaos

    def shutdown(self):
        pass

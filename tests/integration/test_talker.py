import subprocess
import unittest

from talker.client import get_talker


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        redis_container_id = self.get_redis_container_id()
        if not redis_container_id:
            raise Exception('No Redis Container')

        redis_container_ip = self.get_redis_container_ip(redis_container_id)
        self.client = get_talker(redis_container_ip, None, 6379)
        self.client.redis.ping()

    def tearDown(self) -> None:
        self.client.redis.flushall()

    @staticmethod
    def get_redis_container_id():
        return subprocess.check_output(
            'cd tests/integration; docker-compose ps -q redis',
            shell=True,  stderr=subprocess.PIPE).decode('utf-8').strip()

    @staticmethod
    def get_redis_container_ip(redis_container_id):
        shell_cmd = \
            "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' " + redis_container_id
        return subprocess.check_output(shell_cmd, shell=True, stderr=subprocess.PIPE).decode('utf-8').strip()

    def test_echo_hello_command(self):
        cmd = self.client.run('MyHostId', 'bash', '-ce', 'echo hello')
        result = cmd.result()
        self.assertEqual(result, 'hello\n')

    def test_redis_fail(self):
        redis_container_id = self.get_redis_container_id()
        res = subprocess.check_output('docker stop {}'.format(redis_container_id),
                                      shell=True, stderr=subprocess.PIPE).decode('utf-8').strip()
        self.assertEqual(res, redis_container_id)
        res = subprocess.check_output('docker start {}'.format(redis_container_id),
                                      shell=True, stderr=subprocess.PIPE).decode('utf-8').strip()
        self.assertEqual(res, redis_container_id)
        cmd = self.client.run('MyHostId', 'bash', '-ce', 'echo hello')
        result = cmd.result()
        self.assertEqual(result, 'hello\n')

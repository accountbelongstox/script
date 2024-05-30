import subprocess
import threading
from apps.deploy.pyscript.tools.docker import Docker

class DockerDown(Docker):
    def __init__(self):
        pass
        # self.client = docker.from_env()

    # def stop_container(self, container_name):
    #     container = self.client.containers.get(container_name)
    #     container.stop()
    #     print(f"Container {container_name} stopped.")

    def stop_docker(self):
        try:
            subprocess.run(['sudo', 'systemctl', 'stop', 'docker'], check=True)
            print("Docker stopped successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error stopping Docker: {e}")

    def down(self):
        # 创建子线程
        docker_thread = threading.Thread(target=self.stop_docker)

        # 启动子线程
        docker_thread.start()

        # 等待子线程结束
        docker_thread.join()


if __name__ == "__main__":
    docker_down = DockerDown()
    docker_down.down()

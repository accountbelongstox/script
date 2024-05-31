from pycore.utils_linux import file, sysarg
from pycore.practicals_linux import yml
from apps.deploy.pyscript.install.install_choice import install_choice
from apps.deploy.pyscript.install.install_local_choice import install_local_choice
from apps.deploy.pyscript.provider.deployenv import env, compose_env, deploy_dir
from pycore.base.base import Base
import sys,os

# import website

class DeplyMainScript(Base):
    def __init__(self):
        pass

    def test(self):
        from pycore.practicals_linux import env as _env
        print("deploy-test")

    def main(self):
        param_type = sysarg.get_arg(1)
        param_func = sysarg.get_arg(2)

        if param_type is None:
            print("Missing argument: Please provide the parameter type (yml, env, web).")
            return

        if param_type == 'yml':
            if param_func in dir(yml):
                getattr(yml, param_func)(*sys.argv[3:])
            else:
                print(f"'yml' parameter type does not support the function: {param_func}")
            return

        if param_type == 'env':
            if param_func == "get_env":
                env_name = sysarg.get_arg(3)
                val = env.get_env(env_name)
                print(val)
            return

        if param_type == 'install':
            install_choice.install()
            return

        if param_type == 'init_env':
            install_choice.init_env()
            return
        
        if param_type == 'local_install':
            install_local_choice.local_install()
            return
        

        if param_type == 'compiler_docker':
            install_choice.compiler_docker()
            return


        if param_type == 'tool':
            if param_func in dir(self.tool):
                getattr(self.tool, param_func)(*sys.argv[3:])
            else:
                print(f"'env' parameter type does not support the function: {param_func}")
            return

        if param_type == 'docker':
            if param_func in dir(self.tool):
                getattr(self.tool, param_func)(*sys.argv[3:])
            else:
                print(f"'env' parameter type does not support the function: {param_func}")
            return

        # elif param_type == 'web':
        #     if param_func in dir(self.web):
        #         getattr(self.web, param_func)(*sys.argv[3:])
        #     else:
        #         print(f"'web' parameter type does not support the function: {param_func}")

        print(f"Invalid parameter type: {param_type}. Please use 'yml', 'env', or 'web'.")


deploy = DeplyMainScript()

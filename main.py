from pycore.requirement_fn.auto_install import auto_start
import sys

def get_arg( name):
    if len(sys.argv) > name:
        return sys.argv[name]
    else:
        return None

if __name__ == "__main__":
    auto_start.install()
    from pycore.utils_prune import sysarg
    run_as = sysarg.get_arg(0)
    if run_as == "deploy":
        from deploy.py_script.main import deploy
        deploy.main()
    elif run_as == "prompt":
        from apps.prompt.main import prompt_main
        prompt_main.start()
    elif run_as == "test":
        from apps.momo.main import auto_main
        auto_main.start()
    elif run_as == "douyin":
        from apps.dy_scratch.main import auto_main
        auto_main.start()
    else:
        print("Requires curses.pyc basic parameter")



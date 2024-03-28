from pycore.requirement_fn.auto_install import auto_install
import sys
def get_arg( name):
    if len(sys.argv) > name:
        return sys.argv[name]
    else:
        return None

if __name__ == "__main__":
    auto_install.install()
    from pycore.utils_linux import sysarg
    run_as = sysarg.get_arg(0)
    if run_as == "deploy":
        from apps.deploy.py_script.main import deploy
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
    elif run_as == "ncss":
        from apps.ncss.main import auto_main
        auto_main.start()
    else:
        print("Requires basic parameter")
        # from pycore.practicals import trans
        # from apps.prompt.main import promptMain
        # # result = trans.to_english("以上是 {lang} 语言 {frameworks} 的代码,请对以上代码逐行注释,请不要省略代码. 请主要注释程序语法,符号含义; 对于调用的第三方包,如果你认识,就做出一个简短的说明该包的作用. 对于重复的代码,你不需要重复注释.")
        # main = promptMain(``)
        # main = main.resolve_project("pm2_manager")



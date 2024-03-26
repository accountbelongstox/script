<<<<<<< HEAD
from kernel.base.auto_installrequire import auto_install
=======
from pycore.requirement_fn.auto_install import auto_install
>>>>>>> origin/main
auto_install.start()
if __name__ == "__main__":
    from apps.automation.main import auto_main
    auto_main.start()

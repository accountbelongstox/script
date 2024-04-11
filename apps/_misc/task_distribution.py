<<<<<<< HEAD

from pycore.base.requirement_fn.auto_install import auto_install

auto_install.start()
=======
from pycore.base.requirement_fn.auto_install import auto_install

>>>>>>> 0dc90a94e79ba082f5cdec923f012e58e3c739e6

if __name__ == "__main__":
    from apps.prompt.main import promptMain
    main = promptMain()
    main = main.start()
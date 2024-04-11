<<<<<<< HEAD
from pycore.base.requirement_fn.auto_install import auto_install
=======
from pycore.base.requirement_fn import auto_install
>>>>>>> aff269c51514af00846548538e9421414a244f97
auto_install.start()

if __name__ == "__main__":
    from apps.prompt.main import promptMain
    main = promptMain()
    main = main.start()
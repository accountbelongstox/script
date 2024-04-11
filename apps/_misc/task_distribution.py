from pycore.base.requirement_fn.auto_install import auto_install


if __name__ == "__main__":
    from apps.prompt.main import promptMain
    main = promptMain()
    main = main.start()
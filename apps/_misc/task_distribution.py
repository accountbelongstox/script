from kernel.base.auto_installrequire import auto_install
auto_install.start()

if __name__ == "__main__":
    from apps.prompt.main import promptMain
    main = promptMain()
    main = main.start()
from pycore.base.requirement_fn import auto_install
auto_install.start()
if __name__ == "__main__":
    from apps.automation.main import auto_main
    auto_main.start()

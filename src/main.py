import argparse

def main():
    parser = argparse.ArgumentParser(description="Robot Simulation MVC")
    parser.add_argument('mode',
                        choices=['gui', 'cli','vpython'],
                        nargs='?',
                        default='gui',
                        help="Execution mode: gui (default) or cli")
    args = parser.parse_args()

    if args.mode == 'gui':
        import gui_main
        gui_main.run_gui()
    elif args.mode == 'cli' :
        import cli_main
        cli_main.run_cli()
    elif args.mode == 'vpython':
        import vpython_main
        vpython_main.run_vpython()

if __name__ == "__main__":
    main()

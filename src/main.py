import argparse

def main():
    parser = argparse.ArgumentParser(description="Robot Simulation MVC")
    parser.add_argument('mode',
                        choices=['gui', 'cli'],
                        nargs='?',
                        default='gui',
                        help="Execution mode: gui (default) or cli")
    parser.add_argument('--2d', 
                        dest='use_2d', 
                        action='store_true',
                        help="Use legacy 2D mode (default is 3D)")
    args = parser.parse_args()

    if args.mode == 'gui':
        import gui_main
        gui_main.run_gui()
    else:
        import cli_main
        cli_main.run_cli(not args.use_2d)

if __name__ == "__main__":
    main()

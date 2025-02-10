from ui.cli.command_line import CommandLineUI


def main():
    try:
        ui = CommandLineUI()
        ui.start()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

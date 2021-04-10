def main():
    import ubelt as ub
    from hardwareinfo import backend_linux

    backend_linux.motherboard_info()

    cpu_info = backend_linux.parse_cpu_info()
    print(cpu_info['varied']['cpu_mhz'])
    print('cpu_info = {}'.format(ub.repr2(cpu_info, nl=2)))


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/notes/hardwareinfo/__main__.py
    """
    main()

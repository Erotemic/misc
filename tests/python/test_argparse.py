
# NOTES:

# This is from an old version of ~/code/watch/watch/tasks/fusion/fit.py

# Remove parameters that we will fill in with special logic
# Apparently this is hard to do, argparse is such a mess.

# to_remove = ['default_root_dir']
# dest_to_actions = ub.group_items(parser._actions, lambda x: x.dest)
# for rmkey in to_remove:
#     for action in dest_to_actions[rmkey]:
#         parser._remove_action(action)
#         for optstr in action.option_strings:
#             parser._option_string_actions.pop(optstr)
# for grp in parser._action_groups:
#     dest_to_actions = ub.group_items(grp._actions, lambda x: x.dest)
#     for rmkey in to_remove:
#         for action in dest_to_actions[rmkey]:
#             print('action = {!r}'.format(action))
#             grp._actions.remove(action)



def main():
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--foo',  nargs='*')
    # args = parser.parse_known_args()[0]
    # import ubelt as ub
    # print('args.__dict__ = {}'.format(ub.repr2(args.__dict__, nl=1)))

    import ubelt as ub
    import scriptconfig as scfg
    class MyConfig(scfg.DataConfig):
        foo = scfg.Value(None, nargs='*')
    config = MyConfig.cli(argv=['--foo=-bar,none'], strict=True)
    print('config = {}'.format(ub.repr2(config, nl=1)))




if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/test_argparse.py --foo -bar,none
    """
    main()

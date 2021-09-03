
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

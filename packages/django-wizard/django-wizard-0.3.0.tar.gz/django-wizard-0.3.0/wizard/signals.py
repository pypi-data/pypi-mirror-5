from django import dispatch

wizard_pre_save = dispatch.Signal(providing_args=['step_key', 'request'])
wizard_post_save = dispatch.Signal(providing_args=['step_key', 'request'])
wizard_pre_display = dispatch.Signal(providing_args=['step_key', 'request'])
wizard_post_display = dispatch.Signal(providing_args=['step_key', 'request'])
wizard_post_prereq = dispatch.Signal(providing_args=['step_key', 'request'])
wizard_pre_prereq = dispatch.Signal(providing_args=['step_key', 'request'])

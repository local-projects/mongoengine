__all__ = ['mongoengine_signal', 'pre_init', 'post_init', 'pre_save',
           'pre_save_post_validation', 'post_save', 'pre_delete', 'post_delete']


def mongoengine_signal(signal_name):
    def func(f):
        if not hasattr(f, '_mongoengine_signals'):
            f._mongoengine_signals = dict()

        f._mongoengine_signals[signal_name] = True
        return f

    return func


pre_init = mongoengine_signal('pre_init')
post_init = mongoengine_signal('post_init')
pre_save = mongoengine_signal('pre_save')
pre_save_post_validation = mongoengine_signal('pre_save_post_validation')
post_save = mongoengine_signal('post_save')
pre_delete = mongoengine_signal('pre_delete')
post_delete = mongoengine_signal('post_delete')
pre_bulk_insert = mongoengine_signal('pre_bulk_insert')
post_bulk_insert = mongoengine_signal('post_bulk_insert')

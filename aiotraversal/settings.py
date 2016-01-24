import argparse

from zini import Zini


def includeme(config):
    config['settings_ini'] = Zini()

    with_cmd = bool('cmd' in config and config['cmd'].get('parser'))

    if with_cmd:
        parser = config['cmd']['parser']
        parser.add_argument('--settings',
                            metavar='FILE',
                            help='file settings')

    config.include_deferred(setup_settings, with_cmd=with_cmd)


def setup_settings(config, with_cmd):
    if with_cmd:
        settings_file = config['settings']['file'] = config['cmd']['args'].settings
    else:
        settings_file = config['settings'].setdefault('file', None)

    if settings_file:
        settings = config['settings_ini'].read(settings_file)
    else:
        settings = config['settings_ini'].defaults

    for section_name, data in settings.items():
        if section_name == 'app':
            section = config['settings']
        else:
            section = config['settings'].setdefault(section_name, {})

        for key, value in data.items():
            section[key] = value

    if with_cmd and config['cmd']['args'].cmd:
        args = config['cmd']['args']
        settings_cmd = config['settings'].setdefault(args.cmd, {})

        kv = ((k, v)
              for k, v in getattr(args, args.cmd)._get_kwargs()
              if v is not None)

        for key, value in kv:
            if isinstance(value, argparse.Namespace):
                settings_cmd[key] = dict(value._get_kwargs())
            else:
                settings_cmd[key] = value

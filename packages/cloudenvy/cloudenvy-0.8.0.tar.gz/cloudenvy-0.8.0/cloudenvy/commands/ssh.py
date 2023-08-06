import logging

import fabric.api
import fabric.operations

import cloudenvy.envy


class Ssh(cloudenvy.envy.Command):

    def _build_subparser(self, subparsers):
        help_str = 'SSH into your Envy.'
        subparser = subparsers.add_parser('ssh', help=help_str,
                                          description=help_str)
        subparser.set_defaults(func=self.run)

        subparser.add_argument('-n', '--name', action='store', default='',
                               help='Specify custom name for an Envy.')
        return subparser

    def run(self, config, args):
        envy = cloudenvy.envy.Envy(config)

        if envy.ip():
            disable_known_hosts = ('-o UserKnownHostsFile=/dev/null'
                                   ' -o StrictHostKeyChecking=no')
            forward_agent = '-o ForwardAgent=yes'

            options = [disable_known_hosts]
            if envy.forward_agent:
                options.append(forward_agent)

            fabric.operations.local('ssh %s %s@%s' % (' '.join(options),
                                                      envy.remote_user,
                                                      envy.ip()))
        else:
            logging.error('Could not determine IP.')

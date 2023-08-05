import socket
import sys
import termcolor
import traceback

from deployer.cli import CLInterface, Handler, HandlerType
from deployer.service import ActionException
from deployer.console import Console
from itertools import groupby
import deployer

from pygments import highlight
from pygments.formatters import TerminalFormatter as Formatter
from pygments.lexers import PythonTracebackLexer

from inspect import getfile

__all__ = ('Shell', )


# Handler types

class ActionType(HandlerType):
    def __init__(self, color):
        self.color = color
        self.postfix = '*'

def type_of_service(service):
    group = service.get_group()
    return ServiceType(group.color)

def type_of_action(action):
    group = action.get_group()
    return ActionType(group.color)


class ServiceType(HandlerType):
    def __init__(self, color):
        self.color = color

class BuiltinType(HandlerType):
    color = 'cyan'


# Utils for navigation

def find_root_service(service):
    while service.parent:
        service = service.parent
    return service


def create_navigable_handler(call_handler):
    """
    Crete a ShellHandler which has service path completion.
    """
    class PathHandler(ShellHandler):
        is_leaf = True

        @property
        def handler_type(self):
            return type_of_service(self.service)

        def __init__(self, shell, service):
            ShellHandler.__init__(self, shell)
            self.service = service

        def get_subhandler(self, name):
            parent = self.service.parent

            if name == '.':
                return self

            if name == '-' and self.shell.state.can_cdback:
                return PathHandler(self.shell, self.shell.state.previous_service)

            if parent and name == '/':
                root = find_root_service(parent)
                return PathHandler(self.shell, root)

            if parent and name == '..':
                return PathHandler(self.shell, parent)

            for n, s in self.service.get_subservices(include_private=True):
                if name == n:
                    return PathHandler(self.shell, s)

        def complete_subhandlers(self, part):
            parent = self.service.parent

            if '.'.startswith(part):
                yield '.', self

            if '-'.startswith(part) and self.shell.state.can_cdback:
                yield '-', PathHandler(self.shell, self.shell.state.previous_service)

            if parent and '/'.startswith(part):
                root = find_root_service(parent)
                yield '/', PathHandler(self.shell, root)

            if parent and '..'.startswith(part):
                yield ('..', PathHandler(self.shell, parent))

            # Note: when an underscore has been typed, include private too.
            include_private = part.startswith('_')
            for name, s in self.service.get_subservices(include_private=include_private):
                if name.startswith(part):
                    yield name, PathHandler(self.shell, s)

        __call__ = call_handler

    class RootHandler(PathHandler):
        handler_type = BuiltinType()

        def __init__(self, shell):
            PathHandler.__init__(self, shell, shell.state._service)

    return RootHandler

# Handlers

class ShellHandler(Handler):
    def __init__(self, shell):
        self.shell = shell


class GroupHandler(ShellHandler):
    """
    Contains a static group of subhandlers.
    """
    subhandlers = { }

    def complete_subhandlers(self, part):
        for name, h in self.subhandlers.items():
            if name.startswith(part):
                yield name, h(self.shell)

    def get_subhandler(self, name):
        if name in self.subhandlers:
            return self.subhandlers[name](self.shell)


class Version(ShellHandler):
    is_leaf = True
    handler_type = BuiltinType()

    def __call__(self):
        print termcolor.colored('  deployer library, version: ', 'cyan'),
        print termcolor.colored(deployer.__version__, 'red')
        print termcolor.colored('  Host:                      ', 'cyan'),
        print termcolor.colored(socket.gethostname(), 'red')
        print termcolor.colored('  Root service class:        ', 'cyan'),
        print termcolor.colored(self.shell.root_service.__module__, 'red'),
        print termcolor.colored('  <%s>' % self.shell.root_service.__class__.__name__, 'red')


@create_navigable_handler
def Connect(self):
    """
    Open interactive SSH connection with this host.
    """
    from deployer.contrib.services import connect
    from deployer.host_container import HostsContainer
    c = connect.Connect(HostsContainer({ 'host': self.service.hosts._all }))

    # Run as any other action. (Nice exception handling, e.g. in case of NoInput on host selection.)
    Action(c.with_host, self.shell, False)()


@create_navigable_handler
def Find(self):
    def _list_nested_services(service, prefix):
        for name, action in service.get_actions():
            yield '%s %s' % (prefix, termcolor.colored(name, service.get_group().color))

        for name, subservice in service.get_subservices():
            # Check the parent, to avoid loops.
            if subservice.parent == service:
                for i in _list_nested_services(subservice, '%s %s' % (prefix, termcolor.colored(name, subservice.get_group().color))):
                    yield i

    lesspipe(_list_nested_services(self.service, ''), self.shell.pty)


@create_navigable_handler
def Inspect(self):
    """
    Inspection of the current service. Show host mappings and other information.
    """
    console = Console(self.shell.pty)

    def inspect():
        # Print full name
        yield termcolor.colored('  Service:    ', 'cyan') + \
              termcolor.colored(self.service.__repr__(path_only=True), 'yellow')

        # Service class definition created on
        yield termcolor.colored('  Created on: ', 'cyan') + \
              termcolor.colored(self.service._creation_date, 'red')


        # Print mro
        yield termcolor.colored('  Mro:', 'cyan')
        i = 1
        for m in self.service.__class__.__mro__:
            if m.__module__ != 'deployer.service' and m != object:
                yield termcolor.colored('              %i ' % i, 'cyan') + \
                      termcolor.colored('%s.' % m.__module__, 'red') + \
                      termcolor.colored('%s' % m.__name__, 'yellow')
                i += 1

        # File names
        yield termcolor.colored('  Files:', 'cyan')
        i = 1
        for m in self.service.__class__.__mro__:
            if m.__module__ != 'deployer.service' and m != object:
                yield termcolor.colored('              %i ' % i, 'cyan') + \
                      termcolor.colored(getfile(m), 'red')
                i += 1

        # Print host mappings
        yield termcolor.colored('  Hosts:', 'cyan')

        for role in sorted(self.service.hosts._hosts.keys()):
            items = self.service.hosts._hosts[role]
            yield termcolor.colored('         "%s"' % role, 'yellow')
            i = 1
            for host in sorted(items, key=lambda h:h.slug):
                yield termcolor.colored('            %3i ' % i, 'cyan') + \
                      termcolor.colored('%-25s (%s)' % (host.slug, getattr(host, 'address', '')), 'red')
                i += 1

        # Print the first docstring (look to the parents)
        for m in self.service.__class__.__mro__:
            if m.__module__ != 'deployer.service' and m != object and m.__doc__:
                yield termcolor.colored('  Docstring:\n', 'cyan') + \
                      termcolor.colored(m.__doc__ or '<None>', 'red')
                break

        # Actions
        yield termcolor.colored('  Actions:', 'cyan')

        def item_iterator():
            for name, a in self.service.get_actions():
                yield termcolor.colored(name, 'red'), len(name)

        for line in console.in_columns(item_iterator(), margin_left=13):
            yield line

        # Services
        yield termcolor.colored('  Sub services:', 'cyan')

            # Group by service group
        grouper = lambda i:i[1].get_group()
        for group, services in groupby(sorted(self.service.get_subservices(), key=grouper), grouper):
            yield termcolor.colored('         "%s"' % group.__name__, 'yellow')

            # Create iterator for all the items in this group
            def item_iterator():
                for name, s in services:
                    if s.parent == self.service:
                        text = termcolor.colored(name, type_of_service(s).color)
                        length = len(name)
                    else:
                        text = termcolor.colored('%s -> %s' % (name, s.__repr__(path_only=True)), type_of_service(s).color)
                        length = len('%s -> %s' % (name, s.__repr__(path_only=True)))
                    yield text, length

            # Show in columns
            for line in console.in_columns(item_iterator(), margin_left=13):
                yield line

    console.lesspipe(inspect())


@create_navigable_handler
def Cd(self):
    self.shell.state.cd(self.service)


@create_navigable_handler
def Ls(self):
    """
    List subservices and actions in the current service.
    """
    w = self.shell.stdout.write
    console = Console(self.shell.pty)

    def run():
        # Print services
        if self.service.get_subservices():
            yield termcolor.colored(' ** Services **', 'cyan')
            def column_iterator():
                for name, service in self.service.get_subservices():
                    yield termcolor.colored(name, type_of_service(service).color), len(name)
            for line in console.in_columns(column_iterator()):
                yield line

        # Print actions
        if self.service.get_actions():
            yield termcolor.colored(' ** Actions **', 'cyan')
            def column_iterator():
                for name, action in self.service.get_actions():
                    yield termcolor.colored(name, type_of_action(action).color), len(name)
            for line in console.in_columns(column_iterator()):
                yield line

    console.lesspipe(run())

@create_navigable_handler
def SourceCode(self):
    """
    Print the source code of a service.
    """
    import inspect

    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import TerminalFormatter
    from deployer.console import choice, NoInput

    options = []

    for m in self.service.__class__.__mro__:
        if m.__module__ != 'deployer.service' and m != object:
            options.append( ('%s.%s' % (
                  termcolor.colored(m.__module__, 'red'),
                  termcolor.colored(m.__name__, 'yellow')), m) )

    if len(options) > 1:
        try:
            service_class = choice('Choose service definition', options)
        except NoInput:
            return
    else:
        service_class = options[0][1]

    def run():
        try:
            # Retrieve source
            source = inspect.getsource(service_class)

            # Highlight code
            source = highlight(source, PythonLexer(), TerminalFormatter())

            for l in source.split('\n'):
                yield l.rstrip('\n')
        except IOError:
            yield 'Could not retrieve source code.'

    lesspipe(run(), self.shell.pty)

class Exit(ShellHandler):
    """
    Quit the deployment shell.
    """
    is_leaf = True
    handler_type = BuiltinType()

    def __call__(self):
        self.shell.exit()


class Return(ShellHandler):
    """
    Return from a subshell (which was spawned by a previous service.)
    """
    is_leaf = True
    handler_type = BuiltinType()

    def __call__(self):
        self.shell.state = self.shell.state.return_state


class Clear(ShellHandler):
    """
    Clear window.
    """
    is_leaf = True
    handler_type = BuiltinType()

    def __call__(self):
        sys.stdout.write('\033[2J\033[0;0H')
        sys.stdout.flush()


class Service(Handler):
    """
    Service node.
    """
    def __init__(self, service, shell, sandbox):
        self.service = service
        self.sandbox = sandbox
        self.shell = shell

    @property
    def is_leaf(self):
        return self.service._default_action

    @property
    def handler_type(self):
        if not self.service.parent:
            # For the root service, return the built-in type
            return BuiltinType()
        else:
            return type_of_service(self.service)

    def complete_subhandlers(self, part):
        include_private = part.startswith('_')

        if self.service.parent and '..'.startswith(part):
            yield '..', Service(self.service.parent, self.shell, self.sandbox)

        if '/'.startswith(part):
            root = find_root_service(self.service)
            yield '/', Service(root, self.shell, self.sandbox)

        for name, action in self.service.get_actions(include_private=include_private):
            if name.startswith(part):
                yield name, Action(action, self.shell, self.sandbox)

        for name, subservice in self.service.get_subservices(include_private=include_private):
            if name.startswith(part):
                yield name, Service(subservice, self.shell, self.sandbox)

        if self.is_leaf and '&'.startswith(part):
            yield '&', Action(self.service._default_action, self.shell, self.sandbox, fork=True)

    def get_subhandler(self, name):
        if name == '..' and self.service.parent:
            return Service(self.service.parent, self.shell, self.sandbox)

        elif name == '/':
            return Service(find_root_service(self.service), self.shell, self.sandbox)

        elif self.service.has_subservice(name):
            subservice = self.service.get_subservice(name)
            return Service(subservice, self.shell, self.sandbox)

        elif self.service.has_action(name):
            return Action(self.service.get_action(name), self.shell, self.sandbox)

        elif name == '&' and self.is_leaf:
            return Action(self.service.get_action(self.service._default_action), self.shell, self.sandbox, fork=True)

    def __call__(self):
        if self.service._default_action:
            return Action(self.service.get_action(self.service._default_action), self.shell, self.sandbox).__call__()


class Sandbox(Service):
    handler_type = BuiltinType()

    def __init__(self, service, shell):
        Service.__init__(self, service, shell, True)


class Action(Handler):
    """
    Service action node.
    """
    is_leaf = True

    def __init__(self, action, shell, sandbox, *args, **kwargs):
        self.action = action
        self.shell = shell
        self.sandbox = sandbox
        self.args = args
        self.fork = kwargs.get('fork', False)

    @property
    def handler_type(self):
        if self.fork:
            return BuiltinType()
        else:
            return type_of_action(self.action)

    def __call__(self):
        if self.fork:
            def action(pty):
                self._run_action(pty)

            self.shell.pty.run_in_auxiliary_ptys(action)
        else:
            self._run_action(self.shell.pty)

    def _run_action(self, pty):
        # Execute
        sandbox = self.sandbox
        logger_interface = self.shell.logger_interface

        # Command
        command = '%s.%s()' % (self.action.service.__repr__(path_only=True), self.action.name)

        # Report action call to logger interface
        action_callback = logger_interface.log_cli_action(command, sandbox)

        try:
            if sandbox:
                result = self.action(*self.args).sandbox(pty, logger_interface)
            else:
                result = self.action(*self.args).run(pty, logger_interface)

            action_callback.set_succeeded()

            # When the result is a subservice, start a subshell.
            def handle_result(result):
                if isinstance(result, deployer.service.Env):
                    print ''
                    print 'Starting subshell ...'
                    self.shell.state = ShellState(result._service, return_state=self.shell.state)

                # Otherwise, print result
                elif result is not None and not self.action.supress_result:
                    print result

            if isinstance(result, list):
                for r in result:
                    handle_result(r)
            else:
                handle_result(result)

        except ActionException, e:
            action_callback.set_failed(e)

        except Exception, e:
            # Print traceback and return to shell
            print repr(e)
            tb = traceback.format_exc()
            action_callback.set_failed(e, traceback=tb)


    def complete_subhandlers(self, part):
        # Autocompletion for first action parameter
        if not self.args:
            for a in self.action.autocomplete(part):
                yield a, Action(self.action, self.shell, self.sandbox, a)

        # Autocompletion for the & parameter
        if not self.fork and '&'.startswith(part):
            yield '&', Action(self.action, self.shell, self.sandbox, *self.args, fork=True)

    def get_subhandler(self, part):
        # Get subnodes of this Action, this matches to actions with parameters.
        if self.fork:
            # Cannot write anything behind the & operator
            return None
        elif part == '&':
            return Action(self.action, self.shell, self.sandbox, *self.args, fork=True)
        else:
            return Action(self.action, self.shell, self.sandbox, *(self.args + (part,)))


class RootHandler(ShellHandler):
    subhandlers = {
            'cd': Cd,
            'clear': Clear,
            'exit': Exit,
            'find': Find,
            'ls': Ls,
            '--connect': Connect,
            '--inspect': Inspect,
            '--version': Version,
            '--source-code': SourceCode,
    }

    @property
    def current_service(self):
        return Service(self.shell.state._service, self.shell, sandbox=False)

    @property
    def sandboxed_current_service(self):
        return Sandbox(self.shell.state._service, self.shell)

    def complete_subhandlers(self, part):
        """
        Return (name, Handler) subhandler pairs.
        """
        # Default built-ins
        for name, h in self.subhandlers.items():
            if name.startswith(part):
                yield name, h(self.shell)

        # Return when the shell supports it
        if self.shell.state.can_return and 'return'.startswith(part):
            yield 'return', Return(self.shell)

        # Extensions
        for name, h in self.shell.extensions.items():
            if name.startswith(part):
                yield name, h(self.shell)

        # Sandbox
        if 'sandbox'.startswith(part):
            yield 'sandbox', self.sandboxed_current_service

        # Services autocomplete for 'Do' -> 'do' is optional.
        dot = self.current_service
        if '.'.startswith(part):
            yield '.', dot

        for name, h in dot.complete_subhandlers(part):
            yield name, h

    def get_subhandler(self, name):
        # Current service
        if name == '.':
            return self.current_service

        # Default built-ins
        if name in self.subhandlers:
            return self.subhandlers[name](self.shell)

        if self.shell.state.can_return and name == 'return':
            return Return(self.shell)

        if name == 'sandbox':
            return self.sandboxed_current_service

        # Extensions
        if name in self.shell.extensions:
            return self.shell.extensions[name](self.shell)

        # Services autocomplete for 'Do' -> 'do' is optional.
        dot = self.current_service
        return dot.get_subhandler(name)


class ShellState(object):
    """
    When we are moving to a certain position in the service tree.
    """
    def __init__(self, subservice, return_state=None):
        self._return_state = return_state
        self._service = subservice
        self._prev_service = None

    def clone(self):
        s = ShellState(self._service, self._return_state)
        s._prev_service = self._prev_service
        return s

    @property
    def prompt(self):
        # Returns a list of (text,color) tuples for the prompt.
        result = []
        for s in self._service._path + [self._service]:
            if result:
                result.append( ('.', None) )
            result.append( (s._name or '', s.get_group().color) )
        return result

    def cd(self, target_service):
        self._prev_service = self._service
        self._service = target_service

    @property
    def can_return(self):
        return bool(self._return_state)

    @property
    def return_state(self):
        return self._return_state

    @property
    def can_cdback(self):
        return bool(self._prev_service)

    @property
    def previous_service(self):
         return self._prev_service


class Shell(CLInterface):
    """
    Deployment shell.
    """
    def __init__(self, root_service, pty, logger_interface, clone_shell=None, username=None):
        self.root_service = root_service
        self.pty = pty
        self._username = username
        self.logger_interface = logger_interface

        if clone_shell:
            self.state = clone_shell.state.clone()
        else:
            self._reset_navigation()

        # CLI interface
        self.root_handler = RootHandler(self)
        CLInterface.__init__(self, self.pty, self.root_handler)

    def cd(self, cd_path):
        for p in cd_path:
            try:
                self.state.cd(self.state._service.get_subservice(p))
            except AttributeError:
                print 'Unknown path given.'
                return

    @property
    def extensions(self):
        # Dictionary with extensions to the root handler
        return { }

    def _reset_navigation(self):
        self.state = ShellState(self.root_service)

    def exit(self):
        """
        Exit cmd loop.
        """
        if self.state.can_return:
            self.state = self.state.return_state
            self.ctrl_c()
        else:
            super(Shell, self).exit()

    @property
    def prompt(self):
        """
        Return a list of [ (text, color) ] tuples representing the prompt.
        """
        return ([
                    # Username part
                    (self._username if self._username else '', 'cyan'),
                    (' @ ' if self._username else '', 'green'),

                    # 'deployment'
                    (self.root_service.__class__.__name__, 'cyan')
                ]

                # Path
                + self.state.prompt +

                # Prompt sign
                [
                    (' > ', 'cyan')
                ])

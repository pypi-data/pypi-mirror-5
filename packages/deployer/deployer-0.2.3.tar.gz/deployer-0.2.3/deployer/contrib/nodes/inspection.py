from deployer.node import SimpleNode, Node
import termcolor


class AnalyseHost(SimpleNode):
    """
    Analyze a host and find out what it's used for.
    """
    def analyise(self):
        """
        Discover what a host is used for, which role mappings it has
        for every service.
        """
        print termcolor.colored('Showing service::role for every match of %s' % self.host.slug, 'cyan')

        def process_service(service):
            # Grather roles which contain this host in the current service.
            roles = []
            for role in service.hosts.roles:
                if self.host in service.hosts.filter(role):
                    roles.append(role)

            # If roles were found, print result
            if roles:
                print service.__repr__(path_only=True), termcolor.colored(' :: ', 'cyan'), termcolor.colored(', '.join(roles), 'yellow')

            for name, subservice in service.get_subservices():
                if subservice.parent == service: # Avoid cycles
                    process_service(subservice)

        process_service(self.root)
    __call__ = analyise


class Inspection(Node):
    """
    Inspection of all services
    """
    except_peer_services = [ ]

    def print_everything(self):
        """
        Example command which prints all services with their actions
        """
        def print_service(service):
            print
            print '====[ %s ]==== ' % service.__repr__(path_only=True)
            print

            print 'Actions:'
            for name, action in service.get_actions():
                print ' - ', name, action
            print

            for name, subservice in service.get_subservices():
                print_service(subservice)

        print_service(self.root)


    def global_status(self):
        """
        Sanity check.
        This will browse all services for a 'status' method and run it.
        """
        def process_service(service):
            print service.__repr__(path_only=True)

            for name, action in service.get_actions():
                if name == 'status':
                    try:
                        action()
                    except Exception, e:
                        print 'Failed: ', e.message

            for name, subservice in service.get_subservices():
                process_service(subservice)

        process_service(self.root)

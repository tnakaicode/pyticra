from collections import OrderedDict

# sys.setrecursionlimit(10000)

from pyticra.base import Grammar, CommandGrammar
from pyticra.base import Quantity, Ref, Sequence, Struct, Physical


class ObjectRepository(OrderedDict):
    """
    This class represents a TICRA Object Repository (.tor) file.
    """

    def load(self, filename):
        with open(filename, 'r') as f:
            self.update([(physical.display_name, physical)
                         for physical in Grammar.object_repository.parseFile(f)])

    def save(self, filename):
        """
        Write all the class descriptions to a file, which should have
        the .tor extension.
        """
        with open(filename, 'w') as f:
            f.write(str(self))

    def __str__(self):
        return '\n \n'.join([str(physical) for physical in self.values()]) + '\n'

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, super(ObjectRepository, self).__repr__())

    def extract(self, name, source, careful=False):
        obj = source[name]
        if name in self and careful:
            pass
        else:
            self[obj.display_name] = obj
            obj.traverse(lambda name, thing: isinstance(thing, Ref),
                         lambda name, thing: self.extract(thing.name, source, careful))


class CommandInterface(list):
    """
    This class represents a TICRA Command Interface (.tci) file.
    """

    def __init__(self, other=[]):
        super(CommandInterface, self).__init__(other)
        self.batch_commands = []

    def load(self, filename):
        with open(filename, 'r') as f:
            self.parsed = CommandGrammar.command_interface.parseFile(f)
            self.batch_commands.extend(self.parsed.get('batch_commands', []))
            self.extend(self.parsed.get('commands', []))

    def save(self, filename, batch_mode=True):
        """
        Write all the class descriptions to a file, which should have
        the .tci extension.
        """
        with open(filename, 'w') as f:
            if batch_mode:
                f.write(
                    '\n'.join([str(bc) for bc in self.batch_commands]) + '\n\n' + str(self))
            else:
                f.write(str(self))

    def __str__(self):
        return '\n\n'.join(['{} cmd_{}'.format(command, index + 1) for index, command in enumerate(self)] + ['QUIT'])

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               super(CommandInterface, self).__repr__())

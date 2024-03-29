import numpy as np
import os
import json
import pyparsing as p
from os import path
from collections import OrderedDict

basepath = path.dirname(__file__) + "/"


class Project(object):
    """
    This class represents a GRASP project.

    It currently can only create a blank project.
    """

    extensions = {9: 'g9p', 10: 'gxp', 20: 'gxp'}

    def __init__(self, name="Project", version='20.0.0'):
        self.name = str(name)
        self.version = str(version)
        self.tor = ObjectRepository()
        self.tor.load(basepath + "temp.tor")
        self.tci = CommandInterface()
        # self.tci.load(basepath + "temp.tci")

    def create(self, folder):
        """
        Create a new project folder and a working folder, and save the
        project, object, and command files.
        """
        base = os.path.abspath(os.path.join(folder, self.name))
        working = os.path.join(base, 'working')
        os.mkdir(base)
        os.mkdir(working)
        major_version = int(self.version.split('.')[0])
        project_file = os.path.join(base, '{}.{}'.format(self.name,
                                                         self.extensions[major_version]))
        with open(project_file, 'w') as f:
            f.write(str(self))
        tor_file = os.path.join(working, '{}.tor'.format(self.name))
        with open(tor_file, 'w') as f:
            f.write(str(self.tor))
        tci_file = os.path.join(working, '{}.tci'.format(self.name))
        with open(tci_file, 'w') as f:
            f.write(str(self.tci))

    def __str__(self):
        lines = [
            '[Comment]',
            'Project comment',
            '[TOR file]',
            os.path.join('working', '{}.tor'.format(self.name)),
            '[Auxiliary TOR files]',
            '[TCI file]',
            os.path.join('working', '{}.tci'.format(self.name)),
            '[Default units]',
            'GHz m S/m 1',
            '[Project setup]',
            '<!DOCTYPE Project>',
            '<Project version="{}" application="TICRA Tools">'.format(
                self.version),
            ' <Results/>',
            ' <ResultWindows/>',
            ' <WizardData/>',
            ' <view_configuration/>',
            '</Project>'
        ]
        return ''.join(['{}\n'.format(line) for line in lines])


class CommandInterface(list):
    """
    This class represents a TICRA Command Interface (.tci) file.
    """

    def __init__(self, other=[]):
        super(CommandInterface, self).__init__(other)
        self.batch_commands = []

    def load(self, filename):
        with open(filename, 'r') as f:
            self.parsed = Grammar.command_interface.parse_string(f.read()[:-6])
            self.batch_commands.extend(self.parsed.get('batch_commands', []))
            self.extend(self.parsed.get('command', []))

    def save(self, filename, batch_mode=False):
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
        return '\n\n'.join(['{} '.format(command[0]) for command in self.parsed] +
                           ['QUIT'])

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               super(CommandInterface, self).__repr__())


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
        return '{}({})'.format(self.__class__.__name__,
                               super(OrderedDict, self).__repr__())

    def extract(self, name, source, careful=False):
        """
        Add to this instance the named object from the given source
        and all references on which it depends, all the way up the
        tree, overwriting previous objects.

        If careful is False, the traversal will follow all references
        and add the objects to this instance until it encounters only
        objects that have no dependencies, replacing objects that have
        the same name as objects already in this instance. If an
        object dependency is cyclic, the traversal will lead to an
        infinite loop. This should never happen, and it's not clear
        whether GRASP even allows this. (This could happen most easily
        with coordinate systems.)

        If careful is True, the traversal will stop when it encounters
        an object whose name is already a key in this instance, and it
        will not overwrite this object. Using this option with a name
        already in the dictionary has no effect. This avoids an
        infinite loop in the case of a cyclic reference. It is also
        more efficient, since it avoids repeatedly traversing the
        tree. If there are objects in the tree whose references have
        not been imported, a careful traversal will not import these
        references unless other imported objects reference them.

        A repository populated only by calls to this method with
        careful=True should contain all necessary references.
        """
        obj = source[name]
        if name in self and careful:
            pass
        else:
            self[obj.display_name] = obj
            obj.traverse(lambda name, thing: isinstance(thing, Ref),
                         lambda name, thing: self.extract(thing.name, source, careful))


class Grammar(object):
    """
    This class contains the pyparsing grammar for the TICRA .tor and
    .tci file formats.
    """

    # It might be cleaner to have the grammar for each class in the
    # class itself, but this causes scope problems.
    ident = p.Word(p.alphas + '_', p.alphanums + '_.')
    value = p.Forward()
    empty = p.Empty()
    s_int = p.Word(p.nums)
    s_flt = p.Word(p.nums + '.')

    plus_or_minus = p.Literal('+') ^ p.Literal('-')
    number = p.Combine(
        p.Optional(p.Literal('+') ^ p.Literal('-')) +
        p.Word(p.nums) +
        p.Optional('.' + p.Word(p.nums)) +
        p.Optional(p.CaselessLiteral('E') + p.Word(p.nums + '+-', p.nums)) +
        p.Optional(' ')
    )
    quantity = (
        number +
        p.Optional(p.Word(p.alphas, p.alphanums + '-^/' + ' '), default=None) +
        p.Optional(ident)
    )
    quantity.setParseAction(lambda tokens: Quantity(*tokens))

    # Added '.' to handle Brad's EBEX sims. See if this breaks anything.
    # An identifier is no longer a valid Python variable.

    # "ref(val_name)"
    s_ref = (
        "ref" +
        p.Suppress("(") +
        value +
        p.Suppress(")") +
        p.Optional(ident)
    )
    s_ref.setParseAction(lambda tokens: [Ref(tokens[1])])

    # "ref(val_name)" mm
    s_ref_unit = p.Combine(
        "ref" +
        p.Suppress("(") +
        value +
        p.Suppress(")") +
        value
    )
    s_ref_unit.setParseAction(lambda tokens: [Ref(tokens[1])])

    # "ref()"
    s_ref_empty = (
        "ref" +
        p.Suppress("(") +
        p.Suppress(")")
    )
    s_ref_empty.setParseAction(lambda tokens: [Ref("")])

    # sequence(ref(val1), ref(val2), 1.0)
    s_seq_element = p.Combine(value + p.Optional(' ') + p.Optional(ident))
    s_seq = (
        "sequence" +
        p.Suppress("(") +
        p.delimitedList(s_seq_element) +
        p.Suppress(")")
    )
    s_seq.setParseAction(lambda tokens: [Sequence(tokens[1:])])

    # struct(v1: 0.0 mm, v2:  "ref(v2)", v3:  "ref(v3_1)+ref(v3_2)")
    s_struct_element = p.Group(
        ident +
        p.Suppress(":") +
        p.Combine(
            value +
            p.Optional(' ') +
            p.Optional(ident)
        )
    )

    s_struct = (
        "struct" +
        p.Suppress("(") +
        p.delimitedList(s_struct_element) +
        p.Suppress(")")
    )
    s_struct.setParseAction(
        lambda tokens: [Struct((dat[0], dat[1]) for dat in tokens[1:])]
    )

    #  table
    #    (
    #    Lx  "ref(Lx)"      1
    #    Ly  "ref(Ly)"      1
    #    Wx  "ref(Wx)"      1
    #    Wy  "ref(Wy)"      1
    #    Lx  "ref(Lx)"      2
    #    Ly  "ref(Ly)"      2
    #    Wx  "ref(Wx)"      2
    #    Wy  "ref(Wy)"      2
    #    )
    s_table_line = p.Group(p.OneOrMore(value, stopOn=p.LineEnd()))
    s_table_element = p.OneOrMore(s_table_line)
    s_table = (
        "table" +
        p.Suppress("(") +
        s_table_element +
        p.Suppress(")")
    )
    s_table.setParseAction(lambda tokens: [table(tokens[1:])])

    s_table_empty = (
        "table" +
        p.Suppress("(") +
        p.Suppress(")")
    )
    s_table.setParseAction(lambda tokens: [table("")])

    comment = p.QuotedString('"', unquoteResults=False)
    other = p.Word(p.alphanums + r'\/._-')
    s_val = p.Combine('"' + value + '"' + p.Optional(' ') + p.Optional(ident))

    value << (quantity | s_val |
              s_ref_empty | s_ref | s_ref_unit |
              s_struct | s_seq | s_table | s_table_empty |
              other | comment)
    member = p.Group(ident + p.Suppress(":") + value)
    physical = (
        ident + ident +
        p.Suppress('(') +
        p.Optional(p.delimitedList(member)) +
        p.Suppress(')')
    )
    physical.ignore(p.cppStyleComment)  # '// comment'
    physical.ignore(p.pythonStyleComment)  # '# comment'
    physical.setParseAction(
        lambda tokens: [Physical(tokens[0], tokens[1], tokens[2:])]
    )

    object_repository = p.ZeroOrMore(physical) + p.StringEnd()
    object_repository.ignore(p.cppStyleComment)
    object_repository.ignore(p.pythonStyleComment)

    command = (p.Suppress('COMMAND') +
               p.Suppress('OBJECT') +
               ident('target_name') +
               ident('command_name') +
               p.Suppress('(') +
               p.Optional(p.delimitedList(member))('member') +
               p.Suppress(')'))
    command.ignore(p.cppStyleComment)  # '// comment'
    command.ignore(p.pythonStyleComment)  # '# comment'
    command.ignore(p.Literal('&'))
    command.setParseAction(lambda tokens: [Command(tokens['target_name'],
                                                   tokens['command_name'],
                                                   tokens[2:])])
    command.set_name('command')

    function = (p.Suppress('FUNCTION') +
                ident('function_name') +
                p.Optional(p.delimitedList(command))('command_object') +
                p.Suppress('END'))
    function.ignore(p.cppStyleComment)  # '// comment'
    function.ignore(p.pythonStyleComment)  # '# comment'
    function.ignore(p.Literal('&'))
    function.setParseAction(lambda tokens: [Function(tokens['function_name'],
                                                     tokens[1:])])
    function.set_name('function')

    function_call = (ident('function_name') +
                     p.Suppress('(') +
                     p.Suppress(')'))
    function_call.set_name('function_call')

    # Add support for other batch commands.
    batch_command = (p.CaselessLiteral('FILES READ ALL') +
                     other +
                     p.LineEnd().suppress())
    batch_command.setParseAction(lambda tokens: [BatchCommand(tokens)])
    quit_command = p.CaselessLiteral('QUIT')
    group_command = p.Group((command | function | function_call))

    # Add support for multiple QUIT statements.
    command_interface = (p.ZeroOrMore(group_command) + quit_command +
                         p.StringEnd())
    command_interface.ignore(p.cppStyleComment)
    command_interface.ignore(p.pythonStyleComment)


class Function(OrderedDict):
    """
    This class is a container for GRASP functions.

    It inherits from OrderedDict so that it remembers the ordering of its properties.
    """

    def __init__(self, function_name, other={}):
        super(Function, self).__init__(other)
        self.function_name = str(function_name)

    def __str__(self):
        lines = ['FUNCTION {}'.format(self.function_name)]
        for v in self.items():
            lines.append('\t{}'.format(Command(v[0], v[1], v[2:])))
        lines.append('END')
        return ' &\n'.join(lines)

    def __repr__(self):
        return '{}({!r}, {!r}, {{{}}})'.format(self.__class__.__name__,
                                               self.function_name,
                                               '\t'.join(['{}'.format(Command(v[0], v[1], v[2:])) for v in self.items()]))


class Command(OrderedDict):
    """
    This class is a container for GRASP commands.

    It inherits from OrderedDict so that it remembers the ordering of its properties.
    """

    def __init__(self, target_name, command_name, other={}):
        print(target_name, command_name, other)
        super(Command, self).__init__(other)
        self.target_name = str(target_name)
        self.command_name = str(command_name)

    def __str__(self):
        lines = ['COMMAND OBJECT {} {}'.format(
            self.target_name, self.command_name)]
        lines.append('(')
        for k, v in self.items():
            lines.append('  {:16s} : {},'.format(k, v))
        lines[-1] = lines[-1].rstrip(',')
        lines.append(')')
        return ' &\n'.join(lines)

    def __repr__(self):
        print(self.items())
        return 'COMMAND OBJECT {} {} ( {} )'.format(self.target_name,
                                                    self.command_name,
                                                    ",".join([' {} : {}'.format(k, v) for k, v in self.items()]))

    # This code is shared between Command and Physical objects. Fix this.
    # def traverse(self, test, action):
    #    """
    #    Recursively visit all members of this object. See visit() for
    #    parameter meanings.
    #    """
    #    for name, thing in self.iteritems():
    #        self.visit(name, thing, test, action)

    # def visit(self, name, thing, test, action):
    #    """
    #    Recursively visit every member of this object, calling
    #    action(name, thing) if test(name, thing) is True.
    #    """
    #    if test(name, thing):
    #        action(name, thing)
    #    elif isinstance(thing, Sequence):
    #        for index, element in enumerate(thing):
    #            self.visit(index, element, test, action)
    #    elif isinstance(thing, Struct):
    #        for key, value in thing.iteritems():
    #            self.visit(key, value, test, action)


class BatchCommand(list):

    def __str__(self):
        return ' '.join(self)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               super(BatchCommand, self).__repr__())


class CommandGrammar(object):
    """
    This class contains the pyparsing grammar for the TICRA .tor and
    .tci file formats.
    """

    # It might be cleaner to have the grammar for each class in the
    # class itself, but this causes scope problems.
    # Added '.' to handle Brad's EBEX sims. See if this breaks anything.
    # An identifier is no longer a valid Python variable.
    identifier = p.Word(p.alphas + '_', p.alphanums + '_.')
    plus_or_minus = p.Literal('+') ^ p.Literal('-')
    value = p.Forward()
    s_int = p.Word(p.nums)
    s_flt = p.Word(p.nums + '.')

    number = p.Combine(
        p.Optional(plus_or_minus) +
        p.Word(p.nums) +
        p.Optional('.' + p.Word(p.nums)) +
        p.Optional(p.CaselessLiteral('E') + p.Word(p.nums + '+-', p.nums)) +
        p.Optional(' ')
    )
    quantity = (
        number +
        p.Optional(p.Word(p.alphas, p.alphanums + '-^/' + ' '), default=None) +
        p.Optional(identifier)
    )
    quantity.setParseAction(lambda tokens: Quantity(*tokens))

    value = p.Forward()
    elements = p.delimitedList(value)

    s_ref = (
        "ref" +
        p.Suppress("(") +
        value +
        p.Suppress(")")
    )
    s_ref.setParseAction(lambda tokens: [Ref(tokens[1])])

    s_sequence_elements = p.Combine(
        value + p.Optional(' ') + p.Optional(identifier)
    )
    s_sequence = (
        "sequence" +
        p.Suppress("(") +
        p.delimitedList(s_sequence_elements) +
        p.Suppress(")")
    )
    s_sequence.setParseAction(
        lambda tokens: [Sequence(tokens[1:])]
    )

    s_struct_elements = p.Group(
        identifier +
        p.Suppress(":") +
        p.Combine(
            value +
            p.Optional(' ') +
            p.Optional(identifier))
    )
    s_struct = (
        "struct" +
        p.Suppress("(") +
        p.delimitedList(s_struct_elements) +
        p.Suppress(")")
    )
    s_struct.setParseAction(
        lambda tokens: [Struct((dat[0], dat[1]) for dat in tokens[1:])]
    )

    comment = p.QuotedString('"', unquoteResults=False)

    # This could be a filename or just a string. Added '\' to handle EBEX sim.
    # Should convert to unix filename.
    other = p.Word(p.alphanums + r'\/._-')
    s_val = p.Combine(
        '"' + value + '"' + p.Optional(' ') + p.Optional(identifier)
    )
    value << (quantity | s_ref | s_val | s_struct |
              s_sequence | other | comment)

    member = p.Group(identifier + p.Suppress(":") + value)
    command = ("COMMAND OBJECT" +
               identifier +
               identifier +
               p.Suppress('(') +
               p.Optional(p.delimitedList(member)) +
               p.Suppress(')'))
    command.ignore(p.cppStyleComment)  # '// comment'
    command.ignore(p.pythonStyleComment)  # '# comment'
    command.ignore(p.Literal('&'))
    command.setParseAction(
        lambda tokens: [Command(tokens[1], tokens[2], tokens[3:])]
    )

    # Add support for other batch commands.
    batch_command = p.CaselessLiteral(
        'FILES READ ALL') + other + p.LineEnd().suppress()
    batch_command.setParseAction(lambda tokens: [BatchCommand(tokens)])
    quit_command = p.CaselessLiteral('QUIT')

    # Add support for multiple QUIT statements.
    command_interface = p.ZeroOrMore(command) + p.StringEnd()
    command_interface.ignore(p.cppStyleComment)
    command_interface.ignore(p.pythonStyleComment)


class Physical(OrderedDict):
    """
    This class is a lightweight container for GRASP physical objects.

    It inherits from OrderedDict so that it remembers the ordering of its properties.
    """

    def __init__(self, display_name, class_name, other={}):
        super(Physical, self).__init__(other)
        self.display_name = str(display_name)
        self.class_name = str(class_name)

    def __str__(self):
        lines = ['{}  {}  '.format(self.display_name, self.class_name)]
        lines.append('(')
        for k, v in self.items():
            lines.append('  {:16s} : {},'.format(k, v))
        lines[-1] = lines[-1].rstrip(',')
        lines.append(')')
        return '\n'.join(lines)

    def __repr__(self):
        return '{}({!r}, {!r}, {{{}}})'.format(self.__class__.__name__,
                                               self.display_name,
                                               self.class_name,
                                               ', '.join(['{!r}: {!r}'.format(k, v) for k, v in self.iteritems()]))


class Ref(object):
    """
    This class is a wrapper for Physical objects. It stops the
    recursion of __str__ to avoid infinite loops.

    To do: if pointers to actual objects become useful, implement
    __repr__() to stop infinite loops.
    """

    def __init__(self, ref):
        self.set(ref)

    def set(self, ref):
        """
        This allows self.ref to be changed in a lambda statement.
        """
        if isinstance(ref, str):
            self.name = ref
        elif isinstance(ref, Physical):
            self.name = ref.display_name
        else:
            raise ValueError("Invalid Ref: {!r}".format(ref))
        self.ref = ref

    def __str__(self):
        return 'ref({})'.format(self.name)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self.ref)


class Struct(OrderedDict):

    def __str__(self):
        return 'struct({})'.format(', '.join('{}: {}'.format(k, v)
                                             for k, v in self.items()))

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__, super(
                OrderedDict, self).__repr__())


class Sequence(list):

    def __str__(self):
        return 'sequence({})'.format(', '.join(str(j)
                                               for j in (s for s in self)))

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__, super(
                Sequence, self).__repr__())


class table(list):

    def __str__(self):
        return 'table(\n{}\n)'.format('\n'.join(["\t".join(s) for s in line] for line in self[0]))

    def __repr__(self):
        return '{}(\n{}\n)'.format(self.__class__.__name__,
                                   super(table, self).__repr__())


class Quantity(object):
    """
    This class represents a physical quantity that may or may not carry units.
    """

    def __init__(self, number, units=None):
        if isinstance(number, str):
            try:
                self.number = int(number)
            except ValueError:
                self.number = float(number)
        # This should possibly be expanded for numpy number types.
        elif isinstance(number, int) or isinstance(number, float):
            self.number = number
        else:
            raise ValueError("Invalid number: {!r}".format(number))
        # Add logic for allowed units.
        self.units = units

    def __str__(self):
        # This uses a lowercase e for exponential notation; GRASP
        # writes an uppercase E, but can read either. Using repr
        # instead of str for numbers seems to ensure that no rounding
        # occurs.
        if self.units is None:
            return '{!r}'.format(self.number)
        else:
            return '{!r} {}'.format(self.number, self.units)

    def __repr__(self):
        if self.units is None:
            return '{}({!r})'.format(self.__class__.__name__, self.number)
        else:
            return '{}({!r}, {!r})'.format(
                self.__class__.__name__, self.number, self.units)


class TicraTorEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, Ref):
            return str(obj)
        if isinstance(obj, Struct):
            return str(obj)
        if isinstance(obj, Sequence):
            return str(obj)
        if isinstance(obj, Quantity):
            return str(obj)
        if isinstance(obj, Physical):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

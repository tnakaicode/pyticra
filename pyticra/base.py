import pyparsing as p
from collections import OrderedDict


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


class Sequence(list):

    def __str__(self):
        return 'sequence({})'.format(', '.join(str(j)
                                               for j in (s for s in self)))

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__, super(
                Sequence, self).__repr__())


class Struct(OrderedDict):

    def __str__(self):
        return 'struct({})'.format(', '.join('{}: {}'.format(k, v)
                                             for k, v in self.items()))

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__, super(
                OrderedDict, self).__repr__())


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
        return '{}({!r}, {!r}, {{{}}})'.format(self.__class__.__name__, self.display_name,
                                               self.class_name, ', '.join(['{!r}: {!r}'.format(k, v) for k, v in self.items()]))

class Command(OrderedDict):
    """
    This class is a container for GRASP commands.

    It inherits from OrderedDict so that it remembers the ordering of its properties.
    """

    def __init__(self, target_name, command_name, other={}):
        super(Command, self).__init__(other)
        self.target_name = str(target_name)
        self.command_name = str(command_name)

    def __str__(self):
        lines = ['COMMAND OBJECT {} {}'.format(
            self.target_name, self.command_name)]
        lines.append('(')
        for k, v in self.iteritems():
            lines.append('  {:16s} : {},'.format(k, v))
        lines[-1] = lines[-1].rstrip(',')
        lines.append(')')
        return ' &\n'.join(lines)

    def __repr__(self):
        return '{}({!r}, {!r}, {{{}}})'.format(self.__class__.__name__,
                                               self.target_name,
                                               self.command_name,
                                               ', '.join(['{!r}: {!r}'.format(k, v) for k, v in self.iteritems()]))

    # This code is shared between Command and Physical objects. Fix this.
    def traverse(self, test, action):
        """
        Recursively visit all members of this object. See visit() for
        parameter meanings.
        """
        for name, thing in self.iteritems():
            self.visit(name, thing, test, action)

    def visit(self, name, thing, test, action):
        """
        Recursively visit every member of this object, calling
        action(name, thing) if test(name, thing) is True.
        """
        if test(name, thing):
            action(name, thing)
        elif isinstance(thing, Sequence):
            for index, element in enumerate(thing):
                self.visit(index, element, test, action)
        elif isinstance(thing, Struct):
            for key, value in thing.iteritems():
                self.visit(key, value, test, action)


class BatchCommand(list):

    def __str__(self):
        return ' '.join(self)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               super(BatchCommand, self).__repr__())


class Grammar (object):
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
    member = p.Group(identifier + p.Suppress(':') + value)
    members = p.delimitedList(member)

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
    physical = (
        identifier + identifier +
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
               identifier('target_name') +
               identifier('command_name') +
               p.Suppress('(') +
               p.Optional(members)('members') +
               p.Suppress(')') +
               p.CaselessLiteral('cmd_').suppress() +
               p.Word(p.nums)('number'))
    command.ignore(p.cppStyleComment)  # '// comment'
    command.ignore(p.pythonStyleComment)  # '# comment'
    command.ignore(p.Literal('&'))
    command.setParseAction(lambda tokens: [Command(tokens['target_name'],
                                                   tokens['command_name'],
                                                   list(tokens.get('members', [])))])

    # Add support for other batch commands.
    batch_command = p.CaselessLiteral(
        'FILES READ ALL') + other + p.LineEnd().suppress()
    batch_command.setParseAction(lambda tokens: [BatchCommand(tokens)])
    quit_command = p.CaselessLiteral('QUIT')

    # Add support for multiple QUIT statements.
    command_interface = (p.ZeroOrMore(batch_command)('batch_commands') +
                         p.ZeroOrMore(command)('commands') +
                         quit_command +
                         p.StringEnd())
    command_interface.ignore(p.cppStyleComment)
    command_interface.ignore(p.pythonStyleComment)

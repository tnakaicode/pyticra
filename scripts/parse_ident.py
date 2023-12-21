import os
from pyparsing import *

indent_stack = [1]

key = Word(alphas) + Suppress(":")
stmt = Forward()

suite = indentedBlock(stmt, indent_stack)
body = key + suite

pattern = (Word(alphas) + Suppress("(") + Word(alphas) + Suppress(")"))
stmt << pattern


def key_parse_action(toks):
    print("Parsing '%s'..." % toks[0])


key.setParseAction(key_parse_action)
header = Suppress("[") + Literal("test") + Suppress("]")
content = (header + OneOrMore(indentedBlock(body, indent_stack, False)))

contents = Forward()
suites = indentedBlock(content, indent_stack)

extra = Literal("extra") + Suppress(":") + suites
contents << (content | extra)

parser = OneOrMore(contents)

parser.parseFile("./scripts/parse_ident.txt", parseAll=True)
print(parser)

#     Copyright 2013, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

""" Helper functions for parsing the AST nodes and building the Nuitka node tree.

"""

from nuitka.nodes.StatementNodes import (
    StatementsSequence,
    StatementsFrame,
    mergeStatements
)

from nuitka.nodes.NodeBases import NodeBase

from nuitka import Tracing

from logging import warning

import ast

def dump( node ):
    Tracing.printLine( ast.dump( node ) )

def getKind( node ):
    return node.__class__.__name__.split( "." )[-1]

def extractDocFromBody( node ):
    # Work around ast.get_docstring breakage.
    if len( node.body ) > 0 and getKind( node.body[0] ) == "Expr" and getKind( node.body[0].value ) == "Str":
        return node.body[1:], node.body[0].value.s
    else:
        return node.body, None

build_nodes_args3 = None
build_nodes_args2 = None
build_nodes_args1 = None

def setBuildDispatchers( path_args3, path_args2, path_args1 ):
    global build_nodes_args3, build_nodes_args2, build_nodes_args1

    build_nodes_args3 = path_args3
    build_nodes_args2 = path_args2
    build_nodes_args1 = path_args1

def buildNode( provider, node, source_ref, allow_none = False ):
    if node is None and allow_none:
        return None

    try:
        kind = getKind( node )

        if hasattr( node, "lineno" ):
            source_ref = source_ref.atLineNumber( node.lineno )
        else:
            source_ref = source_ref

        if kind in build_nodes_args3:
            result = build_nodes_args3[ kind ](
                provider   = provider,
                node       = node,
                source_ref = source_ref
            )
        elif kind in build_nodes_args2:
            result = build_nodes_args2[ kind ](
                node       = node,
                source_ref = source_ref
            )
        elif kind in build_nodes_args1:
            result = build_nodes_args1[ kind ](
                source_ref = source_ref
            )
        elif kind == "Pass":
            result = None
        else:
            assert False, kind

        if result is None and allow_none:
            return None

        assert isinstance( result, NodeBase ), result

        return result
    except SyntaxError:
        raise
    except:
        warning( "Problem at '%s' with %s." % ( source_ref, ast.dump( node ) ) )
        raise

def buildNodeList( provider, nodes, source_ref, allow_none = False ):
    if nodes is not None:
        result = []

        for node in nodes:
            if hasattr( node, "lineno" ):
                node_source_ref = source_ref.atLineNumber( node.lineno )
            else:
                node_source_ref = source_ref

            entry = buildNode( provider, node, node_source_ref, allow_none )

            if entry is not None:
                result.append( entry )

        return result
    else:
        return []

def buildStatementsNode( provider, nodes, source_ref, frame = False ):
    # We are not creating empty statement sequences.
    if nodes is None:
        return None

    # Build as list of statements, throw away empty ones, and remove useless nesting.
    statements = buildNodeList( provider, nodes, source_ref, allow_none = True )
    statements = mergeStatements( statements )

    # We are not creating empty statement sequences. Might be empty, because e.g. a global
    # node generates not really a statement, or pass statements.
    if not statements:
        return None

    # In case of a frame is desired, build it instead.
    if frame:
        if provider.isExpressionFunctionBody():
            arg_names     = provider.getParameters().getCoArgNames()
            kw_only_count = provider.getParameters().getKwOnlyParameterCount()
            code_name     = provider.getFunctionName()
            guard_mode    = "generator" if provider.isGenerator() else "full"
        else:
            assert provider.isPythonModule()

            arg_names     = ()
            kw_only_count = 0
            code_name     = "<module>" if provider.isMainModule() else provider.getName()
            guard_mode    = "once"


        return StatementsFrame(
            statements    = statements,
            guard_mode    = guard_mode,
            arg_names     = arg_names,
            kw_only_count = kw_only_count,
            code_name     = code_name,
            source_ref    = source_ref
        )
    else:
        return StatementsSequence(
            statements = statements,
            source_ref = source_ref
        )

def makeStatementsSequenceOrStatement( statements, source_ref ):
    """ Make a statement sequence, but only if more than one statement

    Useful for when we can unroll constructs already here, but are not sure if we actually
    did that. This avoids the branch or the pollution of doing it always.
    """

    if len( statements ) > 1:
        return StatementsSequence(
            statements = statements,
            source_ref = source_ref
        )
    else:
        return statements[0]

def makeStatementsSequence( statements, allow_none, source_ref ):
    if allow_none:
        statements = tuple( statement for statement in statements if statement is not None )

    if statements:
        return StatementsSequence(
            statements = statements,
            source_ref = source_ref
        )
    else:
        return None

def makeStatementsSequenceFromStatement( statement ):
    return StatementsSequence(
        statements = ( statement, ),
        source_ref = statement.getSourceReference()
    )

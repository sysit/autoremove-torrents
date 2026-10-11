import ply.yacc as yacc
from . import logger
from .condition import DSL_CONDITIONS
from .condition.base import Comparer
from .conditionlexer import ConditionLexer
from .exception.nosuchcondition import NoSuchCondition
from .exception.syntaxerror import ConditionSyntaxError

class ConditionParser(object):
    # Condition Map (from the central registry)
    _condition_map = DSL_CONDITIONS

    tokens = ConditionLexer.tokens

    # Standard boolean precedence: AND binds tighter than OR,
    # so `A or B and C` means `A or (B and C)`. Use parentheses to override.
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
    )

    op = {
        ConditionLexer.t_LT: Comparer.LT,
        ConditionLexer.t_GT: Comparer.GT,
        ConditionLexer.t_EQ: Comparer.EQ,
    }

    def p_statement(self, t):
        'statement : expression'
        self.remove = t[1]
        self.remain = self._torrent_list.difference(self.remove)

    def p_sub_expression(self, t):
        'expression : LPAREN expression RPAREN'
        t[0] = t[2]

    def p_and_or_expression(self, t):
        '''
        expression : expression AND expression
                    | expression OR expression
        '''
        if t[2] == 'and': # Intersection
            t[0] = t[1].intersection(t[3])
        elif t[2] == 'or': # Union
            t[0] = t[1].union(t[3])

    def p_relation_op(self, t):
        '''
        relation_op : LT
                     | GT
                     | EQ
        '''
        t[0] = t[1]
    
    def p_relation_expression(self, t):
        '''
        expression : STRING relation_op NUMBER
                    | STRING relation_op STRING
        '''
        result = set()
        if t[1] in self._condition_map:
            obj = self._condition_map[t[1]](t[3], self.op[t[2]])
            obj.apply(self._client_status, self._torrent_list)
            result = obj.remove
        else:
            raise NoSuchCondition('The condition \'%s\' is not supported.' % t[1])
        t[0] = result

    def p_error(self, p):
        if p:
            raise ConditionSyntaxError('Syntax Error: Unexpected token \'%s\'.' % p.value)
        else:
            raise ConditionSyntaxError('Syntax Error: Unexpected EOF.')
    
    def __init__(self, expression):
        # Initialize lexer and parser
        self.lexer = ConditionLexer()
        self.parser = yacc.yacc(module=self, optimize=1)
        # Save expression
        self._expression = expression
        # All of the torrents (set in apply())
        self._torrent_list = set()
        self._client_status = None
        # Results (set by p_statement during parse)
        self.remove = set()
        self.remain = set()
        # Logger
        self._logger = logger.Logger.register(__name__)
    
    # Apply this strategy
    def apply(self, client_status, torrents):
        self._torrent_list = set(torrents)
        self._client_status = client_status
        self.parser.parse(self._expression)
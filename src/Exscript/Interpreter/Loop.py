# Copyright (C) 2007 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import Code
from parselib   import Token
from Term       import Term
from Expression import Expression

class Loop(Token):
    def __init__(self, lexer, parser, parent):
        Token.__init__(self, 'Loop', lexer, parser, parent)
        self.during         = None
        self.until          = None
        self.thefrom        = None
        self.theto          = None
        self.list_variables = []
        self.iter_varnames  = []

        # Expect one ore more lists.
        lexer.expect(self, 'keyword', 'loop')
        lexer.expect(self, 'whitespace')
        if not lexer.current_is('keyword', 'while') and \
           not lexer.current_is('keyword', 'until') and \
           not lexer.current_is('keyword', 'from'):
            self.list_variables = [Term(lexer, parser, parent)]
            lexer.next_if('whitespace')
            while lexer.next_if('comma'):
                lexer.skip(['whitespace', 'newline'])
                self.list_variables.append(Term(lexer, parser, parent))
                lexer.skip(['whitespace', 'newline'])

            # Expect the "as" keyword.
            lexer.expect(self, 'keyword', 'as')

            # The iterator variable.
            lexer.next_if('whitespace')
            type, iter_varname = lexer.token()
            lexer.expect(self, 'varname')
            parent.define(**{iter_varname: []})
            self.iter_varnames = [iter_varname]
            lexer.next_if('whitespace')
            while lexer.next_if('comma'):
                lexer.skip(['whitespace', 'newline'])
                type, iter_varname = lexer.token()
                lexer.expect(self, 'varname')
                parent.define(**{iter_varname: []})
                self.iter_varnames.append(iter_varname)
                lexer.skip(['whitespace', 'newline'])

            if len(self.iter_varnames) != len(self.list_variables):
                error = '%s lists, but only %s iterators in loop' % (len(self.iter_varnames),
                                                                     len(self.list_variables))
                lexer.syntax_error(error, self)

        # Check if this is a "from ... to ..." loop.
        if lexer.next_if('keyword', 'from'):
            lexer.expect(self, 'whitespace')
            self.thefrom = Expression(lexer, parser, parent)
            lexer.next_if('whitespace')
            lexer.expect(self, 'keyword', 'to')
            self.theto = Expression(lexer, parser, parent)
            lexer.next_if('whitespace')

            if lexer.next_if('keyword', 'as'):
                lexer.next_if('whitespace')
                type, iter_varname = lexer.token()
                lexer.expect(self, 'varname')
                lexer.next_if('whitespace')
            else:
                iter_varname = 'counter'
            parent.define(**{iter_varname: []})
            self.iter_varnames = [iter_varname]
        
        # Check if this is a "while" loop.
        if lexer.next_if('keyword', 'while'):
            lexer.expect(self, 'whitespace')
            self.during = Expression(lexer, parser, parent)
            lexer.next_if('whitespace')
        
        # Check if this is an "until" loop.
        if lexer.next_if('keyword', 'until'):
            lexer.expect(self, 'whitespace')
            self.until = Expression(lexer, parser, parent)
            lexer.next_if('whitespace')
        
        # End of statement.
        self.mark_end()

        # Body of the loop block.
        lexer.skip(['whitespace', 'newline'])
        self.block = Code.Code(lexer, parser, parent)


    def value(self):
        if len(self.list_variables) == 0 and not self.thefrom:
            # If this is a "while" loop, iterate as long as the condition is True.
            if self.during is not None:
                while self.during.value()[0]:
                    self.block.value()
                return 1

            # If this is an "until" loop, iterate until the condition is True.
            if self.until is not None:
                while not self.until.value()[0]:
                    self.block.value()
                return 1

        # Retrieve the lists from the list terms.
        if self.thefrom:
            lists = [range(self.thefrom.value()[0], self.theto.value()[0])]
        else:
            lists = [var.value() for var in self.list_variables]
        vars  = self.iter_varnames
        
        # Make sure that all lists have the same length.
        for list in lists:
            if len(list) != len(lists[0]):
                msg = 'All list variables must have the same length'
                self.lexer.runtime_error(msg, self)

        # Iterate.
        for i in xrange(len(lists[0])):
            f = 0
            for list in lists:
                self.block.define(**{vars[f]: [list[i]]})
                f += 1
            if self.until is not None and self.until.value()[0]:
                break
            if self.during is not None and not self.during.value()[0]:
                break
            self.block.value()
        return 1


    def dump(self, indent = 0):
        print (' ' * indent) + self.name,
        print self.list_variables, 'as', self.iter_varnames, 'start'
        if self.during is not None:
            self.during.dump(indent + 1)
        if self.until is not None:
            self.until.dump(indent + 1)
        self.block.dump(indent + 1)
        print (' ' * indent) + self.name, 'end.'

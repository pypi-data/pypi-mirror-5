#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------------------------------


from neurounits.visitors.bases.base_actioner_default_ignoremissing import ASTActionerDefaultIgnoreMissing
from neurounits.visitors.bases.base_actioner import SingleVisitPredicate
from neurounits.visitors.bases.base_visitor import ASTVisitorBase
from neurounits.unit_errors import panic
from neurounits.codegen.nmodl.neuron_constants import NeuronSuppliedValues
#from neurounits.visitors.common.ast_symbol_dependancies import VisitorFindDirectSymbolDependance
#from neurounits.visitors.common.ast_symbol_dependancies import VisitorSymbolDependance
from neurounits.visitors.common.ast_symbol_dependancies import VisitorFindDirectSymbolDependance_OLD
from neurounits.ast.astobjects import AssignedVariable, StateVariable, SymbolicConstant, SuppliedValue, InEquality, Parameter
from neurounits.ast import EqnAssignmentByRegime
import string

from mako.template import Template


class ModFileString(object):
    @classmethod
    def DeclareSymbol(self, p,build_parameters):
        unit = build_parameters.symbol_units[p]
        return "%s    ? (Units: %s %s )"%(p.symbol, unit.powerTen, str(type(unit)) )


class ParameterWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ] )

    def ActionParameter(self, n, modfilecontents,  build_parameters, **kwargs):
        modfilecontents.section_PARAMETER.append( ModFileString.DeclareSymbol(n,build_parameters) )


class StateWriter(ASTActionerDefaultIgnoreMissing):

    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ])

    def ActionStateVariable(self, n, modfilecontents,  build_parameters, **kwargs):
        modfilecontents.section_STATE.append( ModFileString.DeclareSymbol(n,build_parameters) )

    def ActionTimeDerivativeByRegime (self, n, modfilecontents, build_parameters, **kwargs):
        s = CStringWriter.Build(n, build_parameters=build_parameters, expand_assignments=False)
        modfilecontents.section_DERIVATIVE.append( s )

    #def ActionEqnSet(self, n, modfilecontents,  build_parameters, **kwargs):
#
#        # A slightly hacky way of writing out the initial conditions:
#        # TODO: FIX THIS!
#
#        for ic in n.initial_conditions:
#            o1 = n.get_terminal_obj(ic.symbol)
#            o2 = n.get_terminal_obj(ic.value)
#            assert build_parameters.symbol_units[o1] == build_parameters.symbol_units[o2]
#
#            s = '%s = %s' % (ic.symbol, ic.value)
            #modfilecontents.section_INITIAL.append(s)


class SuppliedValuesWriter(ASTActionerDefaultIgnoreMissing):



    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self,action_predicates=[ SingleVisitPredicate() ])

    def ActionSuppliedValue(self, n, modfilecontents, build_parameters,  **kwargs):

        # Sanity Check;
        assert n in build_parameters.supplied_values,  " Can't find %s in supplied values[%s]" % (n.symbol,  ",".join([s.symbol for s in build_parameters.supplied_values]) )

        what = build_parameters.supplied_values[n]

        if what == NeuronSuppliedValues.MembraneVoltage:
            modfilecontents.section_ASSIGNED.append('v (millivolt)')
        elif what == NeuronSuppliedValues.Temperature:
            modfilecontents.section_ASSIGNED.append('celsius (degC)')
        else:
            assert False


class ConstantWriter(ASTActionerDefaultIgnoreMissing):

    def __init__(self):
        ASTActionerDefaultIgnoreMissing.__init__(self,action_predicates=[SingleVisitPredicate()])


def unique(seq):
    seen = set()
    for item in seq:
        if item not in seen:
            seen.add(item)
            yield item


class AssignmentWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self,action_predicates=[ SingleVisitPredicate() ])

    def VisitNineMLComponent(self, component, modfilecontents,  build_parameters, **kwargs):
        self.assigment_statements = {}
        ASTActionerDefaultIgnoreMissing.VisitNineMLComponent(self,component,modfilecontents=modfilecontents, build_parameters=build_parameters, **kwargs)


        # The order of writing out assignments is important. There are 3 phases,
        # 1. Initialisation
        # 2. Pre-State Solving
        # 3. Post-State Solving

        # At this stage, we assume that there are no assignments dependant on states depending on
        # further assignments. This can be resolved, but I have not done so here....

        # Lets build a 'rates() function, as is done by NEURON hh.mod.
        # We include all the 'state-variables and supplied values in the parameters:'
        #print
        symbol_map = {
            'V':'v'
        }

        args = list(component.suppliedvalues) + list(component.state_variables)
        arg_symbols = [ symbol_map.get(a.symbol,a.symbol) for a in args] 
        func_arg_string = ','.join( arg_symbols )


        assignment_strs = []

        # For some sanity checking, make sure that we have met all the dependancies of every line:
        resolved_deps = set( args )
        for ass in component.ordered_assignments_by_dependancies:
            print 'Writing assignment for: ', ass
            # Check dependancies:
            for dep in component.getSymbolDependancicesDirect(ass, include_parameters=False):
                #print '  - Checking deps:', dep, resolved_deps
                assert dep in resolved_deps
            if isinstance(ass, (EqnAssignmentByRegime) ):
                resolved_deps.add(ass.lhs)
            else:
                resolved_deps.add(ass)

            s = CStringWriter.Build(ass, build_parameters=build_parameters, expand_assignments=False)
            assignment_strs.append(s)


        modfilecontents.section_FUNCTIONS.append( Template(r"""
PROCEDURE rates( ${func_arg_string} ) {
%for ass in assignment_strs:
    ${ass}
%endfor
}
        """).render(
            func_arg_string=func_arg_string ,
            assignment_strs=assignment_strs
            )
        )


        # And we need to call this function in two places, in the INITIAL block and in the DERIVATIVE BLOCK
        func_call_string = 'rates(%s)' % ','.join( arg_symbols)
        modfilecontents.section_INITIAL.insert( 0, func_call_string)

        if component.state_variables:
            modfilecontents.section_DERIVATIVE.insert( 0, func_call_string)
        modfilecontents.section_BREAKPOINT_pre_solve.insert( 0, func_call_string)









    def ActionEqnAssignmentByRegime(self, n, modfilecontents,  build_parameters, **kwargs):
        s = CStringWriter.Build(n, build_parameters=build_parameters, expand_assignments=False)
        self.assigment_statements[n.lhs] = s



    def ActionAssignedVariable(self, n, modfilecontents, build_parameters,  **kwargs):
        modfilecontents.section_ASSIGNED.append(ModFileString.DeclareSymbol(n,build_parameters))







class FunctionWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self,):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ] )

    def ActionFunctionDefUser(self, o, modfilecontents,  build_parameters,**kwargs):
        if o.funcname in ['exp','sin','fabs','pow']:
            return False

        func_def_tmpl = """
            FUNCTION $func_name ($func_params) $func_unit
            {
                $func_name = $result_string
            }"""

        func_def = string.Template(func_def_tmpl).substitute( {'func_name' :  o.funcname.replace(".","__"),
                                                               'func_params' : ",".join( [ p.symbol for p in o.parameters.values()] ),
                                                               'result_string' : CStringWriter.Build(o.rhs, build_parameters=build_parameters, expand_assignments=False  ),
                                                               'func_unit' : "",
                                                                }  )
        modfilecontents.section_FUNCTIONS.append(func_def)


class OnEventWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self,):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ] )

    def ActionInEventPort(self, o, modfilecontents, build_parameters,  **kwargs):
        #print o
        #print build_parameters.event_function
        #assert False
        if o != build_parameters.event_function:
            return

        # No Arguments:
        assert len( o.parameters ) == 0
        tmpl = """NET_RECEIVE( weight ) \n { $contents \n}"""

        # And lets hope there is only one transition triggered off that
        # port ;)
        print build_parameters
        component = build_parameters.component
        evt_trans = [tr for tr in component._transitions_events if tr.port == o]
        assert len(evt_trans) == 1
        evt_trans = evt_trans[0]



        contents = "\n".join( [ "" + self.ActionOnEventAssignment(a, modfilecontents=modfilecontents, build_parameters=build_parameters, **kwargs ) for a in evt_trans.actions ] )
        txt = string.Template( tmpl).substitute( contents=contents)
        modfilecontents.section_NETRECEIVES.append(txt)

    def ActionOnEventAssignment(self, o, modfilecontents, build_parameters, **kwargs):
        return CStringWriter.Build(o, build_parameters=build_parameters, expand_assignments=False)







class NeuronBlockWriter(object):
    def __init__(self,  component,  build_parameters,  modfilecontents):
        from .neuron_constants import MechanismType#,NEURONMappings
        # Heading
        if build_parameters.mechanismtype == MechanismType.Point:
            modfilecontents.section_NEURON.append("POINT_PROCESS %s" %build_parameters.suffix )
        elif build_parameters.mechanismtype == MechanismType.Distributed:
            modfilecontents.section_NEURON.append("SUFFIX %s" %build_parameters.suffix )
        else:
            assert False


        #current_unit_in_nrn = NEURONMappings.current_units[build_parameters.mechanismtype]
        # Currents:
        for currentSymbol, neuronCurrentObj in build_parameters.currents.iteritems():
            modfilecontents.section_NEURON.append("NONSPECIFIC_CURRENT %s" %currentSymbol.symbol )
            #modfilecontents.section_ASSIGNED.append("%s (%s)"%(currentSymbol.symbol, current_unit_in_nrn ) )




class NeuronInterfaceWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ] )

    def ActionAssignedVariable(self, n, modfilecontents,build_parameters, **kwargs):
        modfilecontents.section_NEURON.append("RANGE %s"%(n.symbol) )

    def ActionStateVariable(self, n, modfilecontents, **kwargs):
        modfilecontents.section_NEURON.append("RANGE %s"%(n.symbol) )

    def ActionParameter(self, n, modfilecontents, **kwargs):
        modfilecontents.section_NEURON.append("RANGE %s"%(n.symbol) )














class CStringWriter(ASTVisitorBase):

    def __init__(self, build_parameters, expand_assignments):
        ASTVisitorBase.__init__(self,)
        self.build_parameters = build_parameters
        self.expand_assignments =expand_assignments


    @classmethod
    def Build (self, lhs, build_parameters, expand_assignments):
        c = CStringWriter(build_parameters = build_parameters,expand_assignments=expand_assignments)
        return c.visit(lhs)

    def VisitIfThenElse(self, o, **kwargs):
        assert isinstance( o.predicate, InEquality), "Only simple if supported"
        return """ifthenelse( %s, %s, %s, %s)"""%(
                self.visit(o.predicate.lesser_than),
                self.visit(o.predicate.greater_than),
                self.visit(o.if_true_ast),
                self.visit(o.if_false_ast) )
        #raise NotImplementedError()
    def VisitInEquality(self, o,**kwargs):
        return "%s < %s"%( self.visit(o.lesser_than), self.visit(o.greater_than))

    def VisitBoolAnd(self, o, **kwargs):
        raise NotImplementedError()
    def VisitBoolOr(self, o, **kwargs):
        raise NotImplementedError()
    def VisitBoolNot(self, o, **kwargs):
        raise NotImplementedError()

    # Function Definitions:
    def VisitFunctionDefUser(self, o, **kwargs):
        panic()

    def VisitFunctionDefBuiltIn(self, o, **kwargs):
        raise NotImplementedError()

    def VisitFunctionDefParameter(self, o, **kwargs):
        return self.GetTerminal(o)



    def GetTerminal(self, n):

        symbol = n.symbol
        if n in self.build_parameters.supplied_values:
            if self.build_parameters.supplied_values[n] is NeuronSuppliedValues.MembraneVoltage:
                symbol = 'v'

        # Term should be in base SI units:
        print n.symbol, type(n)
        #print "Symbols:", [ s.symbol for s in self.build_parameters.symbol_units.keys() ]

        if n.get_dimensionality() == self.build_parameters.symbol_units[n]:
            return symbol

        else:
            multiplier = "(%e)"% 10**self.build_parameters.symbol_units[n].powerTen
            return "%s * %s"%(multiplier, symbol)


    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        return self.GetTerminal(o)
    def VisitParameter(self, o, **kwargs):
        return self.GetTerminal(o)
    def VisitAssignedVariable(self, o, **kwargs):
        if not self.expand_assignments:
            return self.GetTerminal(o)
        else:
            # TODO: Change this to look up the value
            return self.visit( o.assignment_rhs )

    def VisitSuppliedValue(self, o, **kwargs):
        return self.GetTerminal(o)


    def VisitConstant(self, o, **kwargs):
        return "%e"% o.value.float_in_si()

    def VisitSymbolicConstant(self,o , **kwargs):
        return "%e" %o.value.float_in_si()



    # AST Objects:
    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        rhs_si =  self.visit(o.rhs_map)
        lhs =  o.lhs.symbol

        # Check for non-SI assignments to the lhs
        multiplier = ""
        if o.lhs.get_dimensionality() != self.build_parameters.symbol_units[o.lhs]:
            multiplier = "(%e)*"% 10**(-1*self.build_parameters.symbol_units[o.lhs].powerTen)

        # NEURON has a dt in 'ms', so we need to scale from SI.
        return "%s' = (0.001)* %s %s" %( lhs, multiplier, rhs_si )

    def VisitRegimeDispatchMap(self, o, **kwargs):
        assert len(o.rhs_map) == 1
        return self.visit( o.rhs_map.values()[0] )


    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        rhs_si =  self.visit(o.rhs_map)
        lhs =  o.lhs.symbol

        # Check for non-SI assignments to the lhs
        multiplier = ""
        if o.lhs.get_dimensionality() != self.build_parameters.symbol_units[o.lhs]:
            multiplier = "(%e)*"% 10**(-1*self.build_parameters.symbol_units[o.lhs].powerTen)

        return "%s = %s %s" %( lhs, multiplier, rhs_si )


    def VisitOnEventStateAssignment(self, o, **kwargs):
        rhs_si =  self.visit(o.rhs)
        lhs =  o.lhs.symbol

        # Check for non-SI assignments to the lhs
        multiplier = ""
        if o.lhs.get_dimensionality() != self.build_parameters.symbol_units[o.lhs]:
            multiplier = "(%e)*"% 10**(-1*self.build_parameters.symbol_units[o.lhs].powerTen)

        return "%s = %s %s" %( lhs, multiplier, rhs_si )



    def VisitAddOp(self, o, **kwargs):
        return "( %s + %s )"%( self.visit(o.lhs,**kwargs), self.visit(o.rhs, **kwargs) )

    def VisitSubOp(self, o,  **kwargs):
        return "( %s - %s )"%( self.visit(o.lhs,**kwargs), self.visit(o.rhs, **kwargs) )

    def VisitMulOp(self, o, **kwargs):
        return "( %s * %s )"%( self.visit(o.lhs,**kwargs), self.visit(o.rhs, **kwargs) )

    def VisitDivOp(self, o, **kwargs):
        return "( %s / %s )"%( self.visit(o.lhs,**kwargs), self.visit(o.rhs, **kwargs) )

    def VisitExpOp(self, o, **kwargs):
        return "((%s)^%s )"%( self.visit(o.lhs,**kwargs), o.rhs )


    # TODO: HANDLE PROPERLY:
    def _VisitFunctionDefInstantiation(self, o, **kwargs):
        import neurounits
        if isinstance(o.function_def, neurounits.ast.astobjects.FunctionDefBuiltIn):
            print o.function_def.funcname

            if o.function_def.funcname == "__pow__":
                p0_rhs = self.visit(o.parameters['base'].rhs_ast)
                p1_rhs = self.visit(o.parameters['exp'].rhs_ast)
                r = "pow(%s,%s)"%( o.function_def.funcname, p0_rhs, p1_rhs  )
                return r
            

            else:
                assert len(o.parameters) == 1
                p0_rhs = self.visit(o.parameters.values()[0].rhs_ast)
                r = "%s(%s)"%( o.function_def.funcname.replace("__",""), p0_rhs )
                return r


        elif type(o.function_def) == neurounits.ast.astobjects.FunctionDefUser:
            #params = ",".join( self.visit(p.rhs_ast,varnames=varnames, varunits=varunits,**kwargs) for p in o.parameters.values()  )
            #func_call = "%s(%s)"%( varnames[o.function_def].raw_name, params)
            print 'T',  [ type(p.rhs_ast) for p in o.parameters.values()]
            params = ",".join( self.visit(p.rhs_ast) for p in o.parameters.values()  )
            func_call = "%s(%s)"%( o.function_def.funcname.replace(".","__"), params)
            return func_call
        else:
            panic()

    def VisitFunctionDefBuiltInInstantiation(self, o, **kwargs):
        return self._VisitFunctionDefInstantiation(o,**kwargs)
    def VisitFunctionDefUserInstantiation(self, o, **kwargs):
        return self._VisitFunctionDefInstantiation(o,**kwargs)



    def VisitFunctionDefInstantiationParameter(self, o, **kwargs):
        panic()

























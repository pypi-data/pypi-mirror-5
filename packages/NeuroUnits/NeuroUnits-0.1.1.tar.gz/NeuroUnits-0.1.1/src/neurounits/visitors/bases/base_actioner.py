#!/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
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
# -------------------------------------------------------------------------------

import itertools
from .base_visitor import ASTVisitorBase


class SingleVisitPredicate(object):

    def __init__(self):
        self.visited = set()

    def __call__(self, n, **kwargs):
        has_not_visited = n not in self.visited
        self.visited.add(n)
        return has_not_visited


class ASTActionerDepthFirst(ASTVisitorBase):

    def __init__(self, action_predicates=None, **kwargs):
        self.action_predicates = action_predicates or []
        super(ASTActionerDepthFirst, self).__init__(**kwargs)


    def VisitLibraryManager(self, o, **kwargs):
        for c in itertools.chain(o.components, o.libraries):
            self.visit(c)
        self._ActionLibraryManager( o, **kwargs)

    def VisitInterface(self, o, **kwargs):
        self._ActionInterface( o, **kwargs)

    def VisitCompoundPortConnector(self, o, **kwargs):
        self.visit(o.interface_def)
        for wire in o.wire_mappings:
            self.visit(wire)
        self._ActionCompoundPortConnector(o, **kwargs)

    def VisitCompoundPortConnectorWireMapping(self, o, **kwargs):
        self.visit(o.component_port)
        self.visit(o.interface_port)
        self._ActionCompoundPortConnectorWireMapping(o, **kwargs)

    def VisitInterfaceWireContinuous(self, o, **kwargs):
        pass
    def VisitInterfaceWireEvent(self, o, **kwargs):
        pass


    def VisitLibrary(self, o, **kwargs):
        subnodes = itertools.chain(o.functiondefs, o.symbolicconstants)
        for f in subnodes:
            self.visit(f, **kwargs)

        self._ActionLibrary(o, **kwargs)


    def VisitNineMLComponent(self, o, **kwargs):


        self.visit(o._time_node, **kwargs)
        subnodes = set(itertools.chain(o.ordered_assignments_by_dependancies, o.timederivatives, o.functiondefs, o.symbolicconstants, o.transitions, o._event_port_connections, o.rt_graphs, o._interface_connectors))
        for f in subnodes:
            self.visit(f, **kwargs)


        self._ActionNineMLComponent(o, **kwargs)

    #def VisitOnEvent(self, o, **kwargs):
    #    for p in o.parameters.values():
    #        self.visit(p, **kwargs)
    #    for action in o.actions:
    #        self.visit(action, **kwargs)
    #    self._ActionOnEvent(o, **kwargs)

    def VisitOnEventStateAssignment(self, o, **kwargs):
        self.visit(o.lhs, **kwargs)
        self.visit(o.rhs, **kwargs)
        self._ActionOnEventStateAssignment(o, **kwargs)

    def VisitIfThenElse(self, o, **kwargs):
        self.visit(o.predicate, **kwargs)
        self.visit(o.if_true_ast, **kwargs)
        self.visit(o.if_false_ast, **kwargs)
        self._ActionIfThenElse(o, **kwargs)

    def VisitInEquality(self, o, **kwargs):
        self.visit(o.lesser_than, **kwargs)
        self.visit(o.greater_than, **kwargs)
        self._ActionInEquality(o, **kwargs)

    def VisitBoolAnd(self, o, **kwargs):
        self.visit(o.lhs, **kwargs)
        self.visit(o.rhs, **kwargs)
        self._ActionBoolAnd(o, **kwargs)

    def VisitBoolOr(self, o, **kwargs):
        self.visit(o.lhs, **kwargs)
        self.visit(o.rhs, **kwargs)
        self._ActionBoolOr(o, **kwargs)

    def VisitBoolNot(self, o, **kwargs):
        self.visit(o.lhs, **kwargs)
        self._ActionBoolNot(o, **kwargs)


    # Function Definitions:
    def VisitFunctionDefUser(self, o, **kwargs):
        for p in o.parameters.values():
            self.visit(p, **kwargs)
        self.visit(o.rhs, **kwargs)
        self._ActionFunctionDefUser(o, **kwargs)

    def VisitFunctionDefBuiltIn(self, o, **kwargs):
        for p in o.parameters.values():
            self.visit(p, **kwargs)
        self._ActionFunctionDefBuiltIn(o, **kwargs)

    def VisitFunctionDefParameter(self, o, **kwargs):
        self._ActionFunctionDefParameter(o, **kwargs)

    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        if o.initial_value:
            self.visit(o.initial_value)
        self._ActionStateVariable(o, **kwargs)

    def VisitSymbolicConstant(self, o, **kwargs):
        self._ActionSymbolicConstant(o, **kwargs)

    def VisitParameter(self, o, **kwargs):
        self._ActionParameter(o, **kwargs)

    def VisitConstant(self, o, **kwargs):
        self._ActionConstant(o, **kwargs)

    def VisitConstantZero(self, o, **kwargs):
        self._ActionConstantZero(o, **kwargs)

    def VisitAssignedVariable(self, o, **kwargs):
        self._ActionAssignedVariable(o, **kwargs)

    def VisitSuppliedValue(self, o, **kwargs):
        self._ActionSuppliedValue(o, **kwargs)

    def VisitTimeVariable(self, o, **kwargs):
        self._ActionTimeVariable(o, **kwargs)

    def VisitAnalogReducePort(self, o, **kwargs):
        self._ActionAnalogReducePort(o, **kwargs)

    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        self.visit(o.lhs, **kwargs)
        self.visit(o.rhs_map, **kwargs)
        self._ActionTimeDerivativeByRegime(o, **kwargs)

    def VisitRegimeDispatchMap(self, o, **kwargs):
        for rhs in o.rhs_map.values():
            self.visit(rhs, **kwargs)

        for rhs in o.rhs_map.keys():
            self.visit(rhs, **kwargs)

        self._ActionRegimeDispatchMap(o, **kwargs)

    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        self.visit(o.lhs, **kwargs)
        self.visit(o.rhs_map, **kwargs)
        self._ActionEqnAssignmentByRegime(o, **kwargs)

    def VisitAddOp(self, o, **kwargs):
        self.visit(o.lhs, **kwargs)
        self.visit(o.rhs, **kwargs)
        self._ActionAddOp(o, **kwargs)

    def VisitSubOp(self, o, **kwargs):
        self.visit(o.lhs, **kwargs)
        self.visit(o.rhs, **kwargs)
        self._ActionSubOp(o, **kwargs)

    def VisitMulOp(self, o, **kwargs):
        self.visit(o.lhs, **kwargs)
        self.visit(o.rhs, **kwargs)
        self._ActionMulOp(o, **kwargs)

    def VisitDivOp(self, o, **kwargs):
        self.visit(o.lhs, **kwargs)
        self.visit(o.rhs, **kwargs)
        self._ActionDivOp(o, **kwargs)

    def VisitExpOp(self, o, **kwargs):
        self.visit(o.lhs, **kwargs)
        self._ActionExpOp(o, **kwargs)

    def VisitFunctionDefBuiltInInstantiation(self, o, **kwargs):
        for p in o.parameters.values():
            self.visit(p, **kwargs)
        self.visit(o.function_def, **kwargs)
        self._ActionFunctionDefBuiltInInstantiation(o, **kwargs)

    def VisitFunctionDefUserInstantiation(self, o, **kwargs):
        for p in o.parameters.values():
            self.visit(p, **kwargs)
        self.visit(o.function_def, **kwargs)
        self._ActionFunctionDefUserInstantiation(o, **kwargs)




    def VisitFunctionDefInstantiationParameter(self, o, **kwargs):
        self.visit(o.rhs_ast, **kwargs)
        self._ActionFunctionDefInstantiationParameter(o, **kwargs)

    def VisitOnConditionTriggerTransition(self, o, **kwargs):
        self.visit(o.trigger, **kwargs)
        for a in o.actions:
            self.visit(a, **kwargs)
        self._ActionOnConditionTriggerTransition(o, **kwargs)

    def VisitOnCrossesTriggerTransition(self, o, **kwargs):
        self.visit(o.crosses_lhs, **kwargs)
        self.visit(o.crosses_rhs, **kwargs)
        for a in o.actions:
            self.visit(a, **kwargs)
        self._ActionOnCrossesTriggerTransition(o, **kwargs)

    def VisitOnTransitionEvent(self, o, **kwargs):
        for a in o.parameters:
            self.visit(a, **kwargs)
        for a in o.actions:
            self.visit(a, **kwargs)
        self.visit(o.port, **kwargs)
        self._ActionOnTransitionEvent(o, **kwargs)

    def VisitOnEventDefParameter(self, o, **kwargs):
        self._ActionOnEventDefParameter(o, **kwargs)

    def VisitEmitEvent(self, o, **kwargs):
        for a in o.parameters:
            self.visit(a, **kwargs)
        self.visit(o.port, **kwargs)
        self._ActionEmitEvent(o, **kwargs)

    def VisitEmitEventParameter(self, o, **kwargs):
        self.visit(o.port_parameter_obj, **kwargs)
        self.visit(o.rhs, **kwargs)
        self._ActionEmitEventParameter(o, **kwargs)



    def VisitInEventPort(self, o, **kwargs):
        for a in o.parameters:
            self.visit(a, **kwargs)
        self._ActionInEventPort(o, **kwargs)
    def VisitInEventPortParameter(self, o, **kwargs):
        self._ActionInEventPortParameter(o, **kwargs)
    def VisitOutEventPort(self, o, **kwargs):
        for a in o.parameters:
            self.visit(a, **kwargs)
        self._ActionOutEventPort(o, **kwargs)
    def VisitOutEventPortParameter(self, o,  **kwargs):
        self._ActionOutEventPortParameter(o, **kwargs)

    def VisitRTGraph(self, o, **kwargs):
        if o.default_regime:
            assert o.default_regime in o.regimes
        for r in o.regimes:
            self.visit(r, **kwargs)
        self._ActionRTGraph(o, **kwargs)

    def VisitRegime(self, o, **kwargs):
        self._ActionRegime(o, **kwargs)

    def VisitEventPortConnection(self, o, **kwargs):
        self._ActionEventPortConnection(o, **kwargs)




    def VisitRandomVariable(self, o, **kwargs):
        for p in o.parameters:
            self.visit(p, **kwargs)
        self._ActionRandomVariable(o)

    def VisitRandomVariableParameter(self, o, **kwargs):
        self.visit(o.rhs_ast)
        self._ActionRandomVariableParameter(o)

    def VisitAutoRegressiveModel(self, o, **kwargs):
        self._ActionAutoRegressiveModel(o, **kwargs)







    def _ActionPredicate(self, o, **kwargs):
        for p in self.action_predicates:
            if not p(o, **kwargs):
                return False
        return True

    def _ActionLibraryManager(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionLibraryManager(o, **kwargs)

    def _ActionLibrary(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionLibrary(o, **kwargs)

    #def _ActionEqnSet(self, o, **kwargs):
    #    if self._ActionPredicate(o, **kwargs):
    #        return self.ActionEqnSet(o, **kwargs)

    def _ActionNineMLComponent(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionNineMLComponent(o, **kwargs)

    def _ActionIfThenElse(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionIfThenElse(o, **kwargs)

    def _ActionInEquality(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionInEquality(o, **kwargs)

    def _ActionBoolAnd(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionBoolAnd(o, **kwargs)

    def _ActionBoolOr(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionBoolOr(o, **kwargs)

    def _ActionBoolNot(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionBoolNot(o, **kwargs)


    def _ActionFunctionDefUser(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionFunctionDefUser(o, **kwargs)

    def _ActionFunctionDefBuiltIn(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionFunctionDefBuiltIn(o, **kwargs)

    def _ActionFunctionDefParameter(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionFunctionDefParameter(o, **kwargs)

    # Terminals:
    def _ActionStateVariable(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionStateVariable(o, **kwargs)

    def _ActionSymbolicConstant(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionSymbolicConstant(o, **kwargs)

    def _ActionParameter(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionParameter(o, **kwargs)

    def _ActionConstant(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionConstant(o, **kwargs)

    def _ActionConstantZero(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionConstantZero(o, **kwargs)

    def _ActionAssignedVariable(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionAssignedVariable(o, **kwargs)

    def _ActionSuppliedValue(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionSuppliedValue(o, **kwargs)

    def _ActionTimeVariable(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionTimeVariable(o, **kwargs)

    def _ActionAnalogReducePort(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionAnalogReducePort(o, **kwargs)

    def _ActionTimeDerivativeByRegime(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionTimeDerivativeByRegime(o, **kwargs)

    def _ActionRegimeDispatchMap(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionRegimeDispatchMap(o, **kwargs)

    def _ActionEqnAssignmentByRegime(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionEqnAssignmentByRegime(o, **kwargs)

    def _ActionAddOp(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionAddOp(o, **kwargs)

    def _ActionSubOp(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionSubOp(o, **kwargs)

    def _ActionMulOp(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionMulOp(o, **kwargs)

    def _ActionDivOp(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionDivOp(o, **kwargs)

    def _ActionExpOp(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionExpOp(o, **kwargs)

    def _ActionFunctionDefUserInstantiation(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionFunctionDefUserInstantiation(o, **kwargs)
    def _ActionFunctionDefBuiltInInstantiation(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionFunctionDefBuiltInInstantiation(o, **kwargs)

    def _ActionFunctionDefInstantiationParameter(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionFunctionDefInstantiationParameter(o, **kwargs)

    #def _ActionOnEvent(self, o, **kwargs):
    #    if self._ActionPredicate(o, **kwargs):
    #        return self.ActionOnEvent(o, **kwargs)

    def _ActionOnEventStateAssignment(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionOnEventStateAssignment(o, **kwargs)

    def _ActionOnConditionTriggerTransition(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionOnConditionTriggerTransition(o, **kwargs)

    def _ActionOnCrossesTriggerTransition(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionOnCrossesTriggerTransition(o, **kwargs)

    def _ActionOnTransitionEvent(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionOnTransitionEvent(o, **kwargs)

    def _ActionOnEventDefParameter(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionOnEventDefParameter(o, **kwargs)

    def _ActionEmitEvent(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionEmitEvent(o, **kwargs)

    def _ActionEmitEventParameter(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionEmitEventParameter(o, **kwargs)


    def  _ActionInEventPort(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionInEventPort(o, **kwargs)
    def  _ActionInEventPortParameter(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionInEventPortParameter(o, **kwargs)
    def  _ActionOutEventPort(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionOutEventPort(o, **kwargs)
    def  _ActionOutEventPortParameter(self, o,  **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionOutEventPortParameter(o, **kwargs)


    def _ActionRTGraph(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionRTGraph(o, **kwargs)
    def _ActionRegime(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionRegime(o, **kwargs)

    def _ActionEventPortConnection(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionEventPortConnection(o, **kwargs)



    def _ActionInterface(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionInterface(o, **kwargs)


    def _ActionCompoundPortConnectorWireMapping(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionCompoundPortConnectorWireMapping(o, **kwargs)
    def _ActionCompoundPortConnector(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionCompoundPortConnector(o, **kwargs)

    def _ActionRandomVariable(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionRandomVariable(o, **kwargs)
    def _ActionRandomVariableParameter(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionRandomVariableParameter(o, **kwargs)


    def _ActionAutoRegressiveModel(self, o, **kwargs):
        if self._ActionPredicate(o, **kwargs):
            return self.ActionAutoRegressiveModel(o, **kwargs)

    def ActionRandomVariable(self, o, **kwargs):
        raise NotImplementedError()
    def ActionRandomVariableParameter(self, o, **kwargs):
        raise NotImplementedError()



    def ActionEventPortConnection(self, o, **kwargs):

        raise NotImplementedError()


    def ActionRTGraph(self, o, **kwargs):
        raise NotImplementedError()


    def ActionLibrary(self,o, **kwargs):
        raise NotImplementedError()
    def ActionNineMLComponent(self, o, **kwargs):
        raise NotImplementedError()


    def ActionIfThenElse(self, o, **kwargs):
        raise NotImplementedError()

    def ActionInEquality(self, o, **kwargs):
        raise NotImplementedError()

    def ActionBoolAnd(self, o, **kwargs):
        raise NotImplementedError()

    def ActionBoolOr(self, o, **kwargs):
        raise NotImplementedError()

    def ActionBoolNot(self, o, **kwargs):
        raise NotImplementedError()

    # Function Definitions:
    def ActionFunctionDefUser(self, o, **kwargs):
        raise NotImplementedError()

    def ActionFunctionDefBuiltIn(self, o, **kwargs):
        raise NotImplementedError()

    def ActionFunctionDefParameter(self, o, **kwargs):
        raise NotImplementedError()

    # Terminals:
    def ActionStateVariable(self, o, **kwargs):
        raise NotImplementedError()

    def ActionSymbolicConstant(self, o, **kwargs):
        raise NotImplementedError()

    def ActionParameter(self, o, **kwargs):
        raise NotImplementedError()

    def ActionConstant(self, o, **kwargs):
        raise NotImplementedError()

    def ActionAssignedVariable(self, o, **kwargs):
        raise NotImplementedError()

    def ActionSuppliedValue(self, o, **kwargs):
        raise NotImplementedError()

    def ActionAnalogReducePort(self, o, **kwargs):
        print 'self', self
        raise NotImplementedError(self)

    def ActionTimeDerivativeByRegime(self, o, **kwargs):
        raise NotImplementedError()

    def ActionRegimeDispatchMap(self, o, **kwargs):
        raise NotImplementedError()

    def ActionEqnAssignmentByRegime(self, o, **kwargs):
        raise NotImplementedError()

    def ActionAddOp(self, o, **kwargs):
        raise NotImplementedError()

    def ActionSubOp(self, o, **kwargs):
        raise NotImplementedError()

    def ActionMulOp(self, o, **kwargs):
        raise NotImplementedError()

    def ActionDivOp(self, o, **kwargs):
        raise NotImplementedError()

    def ActionExpOp(self, o, **kwargs):
        raise NotImplementedError()

    def ActionFunctionDefUserInstantiation(self, o, **kwargs):
        raise NotImplementedError()

    def ActionFunctionDefBuiltInInstantiation(self, o, **kwargs):
        raise NotImplementedError()


    def ActionFunctionDefInstantiationParameter(self, o, **kwargs):
        raise NotImplementedError()

    def ActionOnConditionTriggerTransition(self, o, **kwargs):
        raise NotImplementedError()

    def ActionOnTransitionEvent(self, o, **kwargs):
        raise NotImplementedError()



    def ActionOnEventStateAssignment(self, o, **kwargs):
        raise NotImplementedError()



    def ActionOutEventPort(self, o, **kwargs):
        raise NotImplementedError()
    def ActionOutEventPortParameter(self, o, **kwargs):
        raise NotImplementedError()
    def ActionInEventPort(self, o, **kwargs):
        raise NotImplementedError()
    def ActionInEventPortParameter(self, o, **kwargs):
        raise NotImplementedError()




    def ActionCompoundPortConnectorWireMapping(self, o, **kwargs):
        print self
        raise NotImplementedError()











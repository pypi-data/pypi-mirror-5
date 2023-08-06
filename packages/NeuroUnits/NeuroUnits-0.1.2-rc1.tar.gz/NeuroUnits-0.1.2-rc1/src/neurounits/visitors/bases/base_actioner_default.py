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

from .base_actioner import ASTActionerDepthFirst


class ASTActionerDefault(ASTActionerDepthFirst):

    def __init__(self, **kwargs):
        ASTActionerDepthFirst.__init__(self, **kwargs)

    def ActionNode(self, n, **kwargs):
        assert False, 'Action node in %s %s' % (type(self), type(n))


    def ActionLibrary(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionNineMLComponent(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionIfThenElse(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionInEquality(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionBoolAnd(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionBoolOr(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionBoolNot(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionFunctionDefUser(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionFunctionDefBuiltIn(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionFunctionDefParameter(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionStateVariable(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionSymbolicConstant(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionParameter(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionConstant(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionConstantZero(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionAssignedVariable(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionSuppliedValue(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)
    
    def ActionTimeVariable(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionAnalogReducePort(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionOnEvent(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionOnEventStateAssignment(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionTimeDerivativeByRegime(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionRegimeDispatchMap(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionEqnAssignmentByRegime(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionAddOp(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionSubOp(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionMulOp(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionDivOp(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionExpOp(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionFunctionDefBuiltInInstantiation(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionFunctionDefUserInstantiation(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionFunctionDefInstantiationParameter(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionRegime(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionOnConditionTriggerTransition(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)
    def ActionOnCrossesTriggerTransition(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionOnTransitionEvent(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionOnEventDefParameter(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionEmitEvent(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionAnalogVisitor(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionEmitEventParameter(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionInterface(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)


    def ActionOutEventPort(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)
    def ActionInEventPort(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)
    def ActionOutEventPortParameter(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)
    def ActionInEventPortParameter(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionRTGraph(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)
    def ActionEventPortConnection(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionInterfaceWireContinuous(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)
    def ActionInterfaceWireEvent(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionCompoundPortConnector(self, o,**kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionCompoundPortConnectorWireMapping(self, o,**kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionLibraryManager(self, o,**kwargs):
        return self.ActionNode(o, **kwargs)


    def ActionRandomVariable(self,o,**kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionRandomVariableParameter(self, o, **kwargs):
        return self.ActionNode(o, **kwargs)

    def ActionAutoRegressiveModel(self,o,**kwargs):
        return self.ActionNode(o, **kwargs)

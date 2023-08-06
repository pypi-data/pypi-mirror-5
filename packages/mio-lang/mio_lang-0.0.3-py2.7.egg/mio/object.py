import sys
from copy import copy
from inspect import getmembers, ismethod

import runtime
from .states import NormalState
from .errors import AttributeError, TypeError
from .utils import format_object, method, Null
from .states import BreakState, ContinueState, ReturnState


class Object(object):

    __slots__ = ("attrs", "parent", "_state", "value", "traits", "behaviors",)

    def __init__(self, value=Null, methods=False):
        super(Object, self).__init__()

        self.attrs = {}
        self.parent = None
        self.value = value

        self.traits = []
        self.behaviors = {}

        self._state = NormalState()

        if methods:
            self.create_methods()

    def create_methods(self):
        keys = self.__class__.__dict__.keys()
        predicate = lambda x: ismethod(x) and getattr(x, "method", False)
        for name, method in getmembers(self, predicate):
            if name in keys:
                self[method.name] = method

    def __hash__(self):
        return hash(self.value)

    def __nonzero__(self):
        return bool(self.value)

    def __eq__(self, other):
        return self.value == getattr(other, "value", other)

    def __cmp__(self, other):
        return cmp(self.value, getattr(other, "value", other))

    def __contains__(self, key):
        return key in self.attrs or key in self.behaviors

    def __delitem__(self, key):
        if key in self.attrs:
            del self.attrs[key]
        elif key in self.behaviors:
            del self.behaviors[key]

    def __getitem__(self, key):
        if key in self.attrs:
            return self.attrs[key]
        elif key in self.behaviors:
            return self.behaviors[key]
        else:
            parent = self.parent
            while parent is not None:
                if key in parent:
                    return parent[key]
                parent = parent.parent

        if hasattr(self, "forward"):
            try:
                return self.forward(key)
            except:
                raise AttributeError("%s has no attribute %r" % (self, key))
        raise AttributeError("%s has no attribute %r" % (self, key))

    def __setitem__(self, key, value):
        self.attrs[key] = value

    def __addtrait__(self, trait):
        attrs = ((k, v) for k, v in trait.attrs.items())
        methods = ((k, v) for k, v in attrs if v.type == "Method")
        behaviors = ((k, v) for k, v in methods if not k in self.attrs)

        self.behaviors.update(behaviors)
        self.traits.append(trait)

    def __deltrait__(self, trait):
        for k, v in trait.attrs.items():
            del self.behaviors[k]
        self.traits.remvoe(trait)

    def __str__(self):
        default = "%s_%s" % (self.type, hex(id(self)))
        return str(self.value) if self.value is not Null else default

    __repr__ = __str__

    def clone(self, value=Null):
        obj = copy(self)

        obj.attrs = {}
        obj.parent = self

        if value is not Null:
            obj.value = value

        return obj

    def forward(self, key):
        return runtime.state.find(key)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def type(self):
        return self.__class__.__name__

    # Attribute Operations

    @method("del")
    def _del(self, receiver, context, m, key):
        key = key.eval(context)
        del receiver[key]
        return runtime.state.find("None")

    @method()
    def has(self, receiver, context, m, key):
        key = key.eval(context)
        if key in receiver:
            return runtime.state.find("True")
        return runtime.state.find("False")

    @method()
    def set(self, receiver, context, m, key, value):
        key = key.eval(context)
        value = value.eval(context)
        receiver[key] = value
        return value

    @method()
    def get(self, receiver, context, m, key, default=None):
        key = key.eval(context)
        default = default.eval(context) if default else runtime.find("None")
        return receiver.attrs.get(key, default)

    # Traits Operations

    @method()
    def uses(self, receiver, context, m, *traits):
        traits = [trait.eval(context) for trait in traits]
        for trait in traits:
            receiver.__addtrait__(trait)
        return receiver

    @method()
    def addTrait(self, receiver, context, m, trait):
        trait = trait.eval(context)
        receiver.__addtrait__(trait)
        return receiver

    @method()
    def delTrait(self, receiver, context, m, trait):
        trait = trait.eval(context)
        receiver.__deltrait__(trait)
        return receiver

    @method()
    def hasTrait(self, receiver, context, m, trait):
        trait = trait.eval(context)
        test = trait in receiver.traits
        return runtime.find("True") if test else runtime.find("False")

    @method("traits")
    def getTraits(self, receiver, context, m):
        return runtime.find("List").clone(receiver.traits)

    @method("behaviors")
    def getBehaviors(self, receiver, context, m):
        return runtime.find("List").clone(receiver.behaviors.keys())

    # Block Operations

    @method()
    def block(self, receiver, context, m, *args):
        args, body = args[:-1], args[-1:][0]

        # Evaluate kwargs first
        ctx = runtime.find("Object").clone()
        kwargs = dict([(arg.name, arg.eval(ctx, context)) for arg in args if arg.name == "set"])

        args = [arg.name for arg in args if not arg.name == "set"]

        from .block import Block
        return Block(body, args, kwargs, context)

    @method("method")
    def _method(self, receiver, context, m, *args):
        args, body = args[:-1], args[-1:][0]

        # Evaluate kwargs first
        ctx = runtime.find("Object").clone()
        kwargs = dict([(arg.name, arg.eval(ctx, context)) for arg in args if arg.name == "set"])

        args = [arg.name for arg in args if not arg.name == "set"]

        from .block import Block
        return Block(body, args, kwargs)

    # Flow Control

    @method()
    def foreach(self, receiver, context, m, *args):
        try:
            result = runtime.find("None")
            vars, expression = args[:-1], args[-1]

            for item in receiver:
                if context.state.isContinue:
                    context.state = NormalState()
                    continue

                if len(vars) == 2:
                    context[vars[0].name], context[vars[1].name] = item
                elif len(vars) == 1:
                    context[vars[0].name] = item

                result = expression.eval(context)

                if context.state.stop:
                    return context.state.returnValue
            return result
        finally:
            context.state = NormalState()

    @method("while")
    def _while(self, receiver, context, m, condition, expression):
        try:
            result = runtime.find("None")

            while condition.eval(context):
                if context.state.isContinue:
                    context.state = NormalState()
                    continue

                result = expression.eval(context)

                if context.state.stop:
                    return context.state.returnValue
            return result
        finally:
            context.state = NormalState()

    @method("continue")
    def _continue(self, receiver, context, m):
        context.state = ContinueState()
        return runtime.find("None")

    @method("break")
    def _break(self, reciver, context, m):
        context.state = BreakState()
        return runtime.find("None")

    @method("return")
    def _return(self, receiver, context, m, *args):
        value = args[0].eval(context) if args else runtime.find("None")
        context.state = ReturnState(value)
        return receiver

    # I/O

    @method("print")
    def _print(self, receiver, context, m):
        sys.stdout.write("%s" % receiver.value)
        return receiver

    @method()
    def println(self, receiver, context, m):
        sys.stdout.write("%s\n" % receiver.value)
        return receiver

    @method()
    def write(self, receiver, context, m, *args):
        args = [arg.eval(context) for arg in args]
        sys.stdout.write("".join([str(arg) for arg in args]))
        return runtime.find("None")

    @method()
    def writeln(self, receiver, context, m, *args):
        args = [arg.eval(context) for arg in args]
        sys.stdout.write("".join([str(arg) for arg in args]))
        sys.stdout.write("\n")
        return runtime.find("None")

    # Introspection

    @method("state")
    def __state(self, receiver, context, m):
        TrueValue = runtime.find("True")
        FalseValue = runtime.find("False")

        obj = self.clone()

        obj["type"] = runtime.find("String").clone(self.state.__class__.__name__)

        obj["isContinue"] = TrueValue if self.state.isContinue else FalseValue
        obj["isReturn"] = TrueValue if self.state.isReturn else FalseValue
        obj["isNormal"] = TrueValue if self.state.isNormal else FalseValue
        obj["isBreak"] = TrueValue if self.state.isBreak else FalseValue

        obj["returnValue"] = self.state.returnValue

        return obj

    @method("parent")
    def _parent(self, receiver, context, m):
        if receiver.parent is not None:
            return receiver.parent
        return receiver

    @method("type")
    def _type(self, receiver, context, m):
        return runtime.find("String").clone(receiver.type)

    @method("value")
    def _value(self, receiver, context, m):
        if receiver.value is not Null:
            return receiver.value
        return runtime.find("None")

    @method()
    def hash(self, receiver, context, m):
        return runtime.find("Number").clone(hash(receiver))

    @method()
    def id(self, receiver, context, m):
        return runtime.find("Number").clone(id(receiver))

    @method()
    def keys(self, receiver, context, m):
        String = runtime.find("String")
        keys = [String.clone(key) for key in receiver.attrs.keys()]
        return runtime.find("List").clone(keys)

    @method()
    def summary(self, receiver, context, m):
        sys.stdout.write("%s\n" % format_object(receiver))
        return receiver

    # Object Operations

    @method()
    def evalArg(self, receiver, context, m, arg):
        return arg.eval(receiver, context)

    @method()
    def do(self, receiver, context, m, expression):
        expression.eval(receiver)
        return receiver

    @method()
    def super(self, receiver, context, m):
        return receiver["self"].parent

    @method("clone")
    def _clone(self, receiver, context, m, *args):
        object = receiver.clone()

        try:
            m = runtime.find("Message").clone()
            m.name = "init"
            m.args = args
            m.eval(object, context)
        except AttributeError:
            pass

        return object

    @method()
    def setParent(self, receiver, context, m, parent):
        parent = parent.eval(context)
        if parent is receiver:
            raise TypeError("Canoot set parent to self!")

        receiver.parent = parent

        return receiver

    @method()
    def setValue(self, receiver, context, m, value):
        receiver.value = value.eval(context)
        return receiver

    # Boolean Operations

    @method()
    def cmp(self, receiver, context, m, other):
        return runtime.find("Number").clone(cmp(receiver, other.eval(context)))

    @method("and")
    def _and(self, receiver, context, m, other):
        return self.clone(receiver and other.eval(context))

    @method("or")
    def _or(self, receiver, context, m, other):
        return self.clone(receiver or other.eval(context))

    @method("not")
    def _not(self, receiver, context, m, value=None):
        value = value.eval(context) if value is not None else receiver
        test = not bool(value)
        return runtime.find("True") if test else runtime.find("False")

    # Type Conversion

    @method("bool")
    def bool(self, receiver, context, m):
        return runtime.find("True") if receiver else runtime.find("False")

    @method("repr")
    def repr(self, receiver, context, m):
        return runtime.find("String").clone(repr(receiver))

    @method("str")
    def str(self, receiver, context, m):
        return runtime.find("String").clone(str(receiver))

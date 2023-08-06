from os import path


from mio import runtime
from mio.object import Object
from mio.utils import method, Null


class Module(Object):

    def __init__(self, value=Null):
        super(Module, self).__init__(value=value)

        self.file = None
        self.name = None

        self.create_methods()
        self.parent = runtime.find("Object")

    def __repr__(self):
        return "Module(name={0:s}, file={1:s})".format(repr(self.name), repr(self.file))

    @method()
    def init(self, receiver, context, m, name, file):
        receiver.name = name = str(name.eval(context))
        receiver.file = file = str(file.eval(context))

        # Are we loading a package module?
        if path.isdir(file):
            file = path.join(file, "__init__.mio")

        runtime.state.load(file, receiver, receiver)

        return receiver

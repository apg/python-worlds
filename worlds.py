"""worlds.py: inspired by Alessandro Warth's worlds

Author: Andrew Gwozdziewycz <web@apgwoz.com>
"""

from __future__ import with_statement
import sys, inspect

class InUniverseAlready(Exception):
    """Raised when already in Universe"""

class NoWorldBelow(Exception):
    """No world to pop to"""

class NotSet:
    """A value different than None to avoid NameError"""

class Universe(object):
    """A context manager which establishes an initial world as thisWorld
    """
    in_universe = False
    def __init__(self):
        self._oldThisWorld = NotSet

    def __enter__(self):
        if Universe.in_universe:
            raise InUniverseAlready()

        # not thread safe
        Universe.in_universe = True
        frame = inspect.currentframe().f_back
        if 'thisWorld' in frame.f_locals:
            self._oldThisWorld = frame.f_locals['thisWorld']

        frame.f_locals['thisWorld'] = World()

    def __exit__(self, type, value, traceback):
        try:
            frame = inspect.currentframe().f_back
            if self._oldThisWorld != NotSet:
                frame.f_locals['thisWorld'] = self._oldThisWorld
        finally:
            Universe.in_universe = False

    def __repr__(self):
        return '<Universe at %x>' % id(self)

class World(object):
    __slots__ = ('_parent', '_oldThisWorld', 'locals')
    def __init__(self, parent=None):
        if parent and not isinstance(parent, World):
            raise TypeError("Not a World")
        self._parent = parent
        self._oldThisWorld = NotSet
        self.locals = {}
        
    def pop(self):
        if self._parent:
            return self._parent
        raise NoWorldBelow()
            
    def sprout(self):
        return World(parent=self)

    def commit(self):
        """Update all the variables in the world in the parent"""
        if self._parent:
            for k, v in self.locals.items():
                self._parent.locals[k] = v
        else:
            # since there's no parent, we want to commit to the actual 
            # environment.
            frame = inspect.currentframe().f_back
            for k, v in self.locals.items():
                frame.f_locals[k] = v

    def __setattr__(self, name, value):
        if name in World.__slots__:
            super(World, self).__setattr__(name, value)
        else:
            self.locals[name] = value
            
    def lookup(self, name):
        if name in self.locals:
            return self.locals[name]
        elif self._parent:
            return self.parent.lookup(name)
        raise AttributeError(name)

    def __getattr__(self, name):
        return self.lookup(name)

    def __enter__(self):
        """Enters this world by making thisWorld refer to self"""
        frame = inspect.currentframe().f_back
        if 'thisWorld' in frame.f_locals:
            self._oldThisWorld = frame.f_locals['thisWorld']
        frame.f_locals['thisWorld'] = self
        return self

    def __exit__(self, type, value, traceback):
        """Leaves a world by restoring thisWorld to it's previous value"""
        if self._oldThisWorld != NotSet:
            frame = inspect.currentframe().f_back
            frame.f_locals['thisWorld'] = self._oldThisWorld

    def __repr__(self):
        if self._parent:
            insert = 'world'
        else:
            insert = 'None'
        return '<World: parent=%s>' % insert

if __name__ == '__main__':
    with Universe():
        thisWorld.bigfat = True
        thisWorld.coward = False

        new = thisWorld.sprout()
        new.coward = True
        print 'new == thisWorld?', new == thisWorld

        with new.sprout():
            thisWorld.never_defined = "this should raise a NameError later"

        print 'coward yet in this world?', thisWorld.coward
        new.commit()
        thisWorld.commit()

    print "Is bigfat (%s)and coward (%s)?" % (bigfat, coward)
    
    print "NameError raised here, since never_defined was never committed to the world with no parent (the one introduced by the Universe)", never_defined

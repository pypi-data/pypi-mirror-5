__author__ = 'Bojan Delic <bojan@delic.in.rs>'
__date__ = 'Aug 21, 2013'
__copyright__ = 'Copyright (c) 2013 Bojan Delic'


from functools import partial
from Queue import Queue
from threading import Lock
from collections import defaultdict
import wpf

from System import TimeSpan
from System.Windows.Input import ICommand
from System import EventArgs
from System.Windows.Threading import DispatcherTimer
from System.ComponentModel import INotifyPropertyChanged, PropertyChangedEventArgs


class _Messenger(object):
    '''
    Thread-safe messenger that ensures that all message handlers are executed
    in main dispatcher thread.
    '''
    def __init__(self, interval=5):
        '''
        :param int interval:
            Number of milliseconds that represents interval when messages will
            be processed.
        '''
        self._subscribers = defaultdict(list)
        self._messages = Queue()
        self._lock = Lock()
        self._timer = DispatcherTimer()
        self._timer.Interval = TimeSpan.FromMilliseconds(5)
        self._timer.Tick += self._execute
        self._timer.Start()

    def send(self, message):
        '''
        Sends provided message to all listeners. Message is only added to
        queue and will be processed on next tick.

        :param Message message:
            Message to send.
        '''
        self._messages.put(message, False)

    def subscribe(self, msg, handler):
        '''
        Adds hander for specified message.

        :param str msg:
            Name of message to subscribe to.

        :param callable handler:
            Handler for this message type. Handler must receive single parameter
            and that parameter will be instance of sent message.
        '''
        with self._lock:
            self._subscribers[msg].append(handler)

    def unsubscribe(self, msg, handler):
        '''
        Removes handler from message listeners.

        :param str msg:
            Name of message to unsubscribe handler from.

        :param callable handler:
            Callable that should be removed as handler for `msg`.
        '''
        with self._lock:
            self._subscribers[msg].remove(handler)

    def _execute(self, sender, event_args):
        '''
        Event handler for 
        '''
        with self._lock:
            while not self._messages.empty():
                msg = self._messages.get(False)
                for subscriber in self._subscribers[msg.msg]:
                    subscriber(msg)


class Message(object):
    '''
    Peace of information sent through messaging system.
    '''
    def __init__(self, msg, data=None, callback=None):
        '''
        :param str msg:
            Name of message that will be sent. This name must match to
            names that subscribers used for them to get the message.

        :param object data:
            Any additional data provided with message.

        :param callable callback:
            Callback that handler can choose to call during message processing.
        '''
        self.msg = msg
        self.data = data
        self.callable = callable


class notifiable(property):
    '''
    Decorator that replaces @property decorator by adding raising
    property changed event when setter is invoked.

    Example of usage::

        class MyViewModel(ViewModel):
            @notify_property
            def foo(self):
                return self._foo
            @foo.setter
            def foo(self, val):
                self._foo = val

    For simple properties without getter and setter function and with
    automatic event raising :class:`.NotifyProperty` can be used.

    Idea and initial code for this is taken from
    http://gui-at.blogspot.com/2009/11/inotifypropertychanged-in-ironpython.html
    '''
    def __init__(self, getter):
        def newgetter(slf):
            try:
                return getter(slf)
            except AttributeError:
                return None
        super(notify_property, self).__init__(newgetter)

    def setter(self, setter):
        def newsetter(slf, newvalue):
            oldvalue = self.fget(slf)
            if oldvalue != newvalue:
                setter(slf, newvalue)
                slf.RaisePropertyChanged(setter.__name__)
        return property(fget=self.fget,
            fset=newsetter,
            fdel=self.fdel,
            doc=self.__doc__)


class Notifiable(object):
    '''
    Descriptor class that raises `PropertyChanged` event when new value is
    set. For this to work, this descriptor can only be used in classes that
    implements interface `INotifyPropertyChanged`

    Class is designed to work with subclasses of :class:`ViewModel`
    because this class implements `INotofyPropertyChanged` and adds metaclass
    that discovers names of variables for raising events.

    Example of usage::

        class MyViewModel(ViewModel):
            my_property = NotifProperty()
    '''
    def __init__(self, initial=None, name=None):
        '''
        :param initial:
            Initial value of this property.

        :param name:
            Name of this property. If not provided and if this is used with
            :class:`.ViewModel`, name will be set automatically to name
            of property.
        '''
        self.name = name
        self.initial = initial

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, '__notifiable_%s' % self.name, self.initial)

    def __set__(self, obj, value):
        current = getattr(obj, '__notifiable_%s' % self.name, self.initial)
        if current != value:
            setattr(obj, '__notifiable_%s' % self.name, value)
            obj.RaisePropertyChanged(self.name)


class ViewModelMeta(type):
    '''
    MetaClass that examines fields of new class and populates names of
    :class:`.NotifProperty` fields to names of variables.
    '''
    def __new__(cls, name, bases, dct):
        super_new = super(ViewModelMeta, cls).__new__
        for name, val in dct.items():
            if isinstance(val, Notifiable):
                if not hasattr(val, 'name') or not val.name:
                    val.name = name
        return super_new(cls, name, bases, dct)


class ViewModel(object, INotifyPropertyChanged):
    '''
    Base ViewModel class that all view-model classes should inherit from.
    '''
    __metaclass__ = ViewModelMeta

    def __init__(self):
        self.property_chaged_handlers = []
        self.messenger = _Messenger()

    def RaisePropertyChanged(self, property_name):
        '''
        Raises event that property value has changed for provided property name.

        :param str property_name:
            Name of property whose value has changed.
        '''
        args = PropertyChangedEventArgs(property_name)
        for handler in self.property_chaged_handlers:
            handler(self, args)

    def add_PropertyChanged(self, handler):
        self.property_chaged_handlers.append(handler)

    def remove_PropertyChanged(self, handler):
        self.property_chaged_handlers.Remove(handler)


class Command(ICommand):
    '''
    Implementation of WPF command.
    '''
    def __init__(self, execute, can_execute=None):
        self.execute = execute
        self.can_execute = can_execute
        self._can_execute_changed_handlers = []

    def Execute(self, parameter):
        '''
        Executes handler for this command.
        '''
        self.execute()

    def add_CanExecuteChanged(self, handler):
        '''
        Adds new listener to CanExecuteChanged event.
        '''
        self._can_execute_changed_handlers.append(handler)

    def remove_CanExecuteChanged(self, handler):
        '''
        Removes listener for CanExecuteChanged event.
        '''
        self._can_execute_changed_handlers.remove(handler)

    def RaiseCanExecuteChanged(self):
        '''
        Raises CanExecuteChanged event.
        '''
        for handler in self._can_execute_changed_handlers:
            handler(self, EventArgs.Empty)

    def CanExecute(self, parameter):
        '''
        Returns `True` if command can be executed, `False` otherwise.
        '''
        if self.can_execute:
            return self.can_execute()
        return True


class command(object):
    '''
    Decorator to that turns method to command handler. Example of usage::

        class MyClass(ViewModel):
            @command
            def command_handler(self):
                # do something
                pass
            @command_handler.can_execute
            def command_can_execute(self):
                # return True if command can execute, False otherwise
                return True
    '''
    def __init__(self, handler, can_execute=None):
        '''
        :param callable handler:
            Method that will be called when command executed.

        :param callable can_execute:
            Method that will be called when GUI needs information if command
            can be executed. If not provided, default implementation always
            returns `True`.
        '''
        self._handler = handler
        self._can_execute = can_execute
        self._command = None

    def __get__(self, obj, objtype):
        if not self._handler:
            raise AttributeError('Unable to get field')
        if not self._command:
            self._command = Command(partial(self._handler, obj),
                                    partial(self._can_execute, obj) if self._can_execute else None)
        return self._command

    def can_execute(self, can_execute):
        '''
        Decorator that adds function that determines if command can be executed.

        Decorated function should return `True` if command can be executed
        and false if it can not.
        '''
        self._can_execute = can_execute

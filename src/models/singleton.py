"""
Singleton Design Pattern Implementation

This module provides a Singleton base class and a decorator function for
implementing the Singleton pattern in different contexts.
"""

class Singleton:
    """
    A base class for implementing the Singleton design pattern.
    
    Classes that inherit from this will have only one instance created,
    and all subsequent instance creations will return the same instance.
    
    Note: This should NOT be used with QObject-derived classes due to metaclass conflicts.
    For QObject-derived classes, use the qt_singleton() function instead.
    """
    
    _instances = {}
    
    def __new__(cls, *args, **kwargs):
        # If an instance of this class doesn't exist, create one
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(cls)
        # Return the existing instance
        return cls._instances[cls]

def qt_singleton(cls):
    """
    A decorator function to implement the Singleton pattern for QObject-derived classes.
    
    This function adds a _instance class attribute and an instance() classmethod
    to create and access the singleton instance.
    
    Usage:
    @qt_singleton
    class MyQObjectClass(QObject):
        pass
        
    # Get the singleton instance
    instance = MyQObjectClass.instance()
    """
    
    # Store the original __init__ method
    original_init = cls.__init__
    # Initialize the singleton instance to None
    cls._instance = None
    
    # Define a new __init__ that only initializes the first time
    def __init__(self, *args, **kwargs):
        # Always call original_init to ensure proper initialization
        original_init(self, *args, **kwargs)
    
    # Define the instance classmethod to retrieve the singleton
    def instance(cls, *args, **kwargs):
        if cls._instance is None:  # pragma: no cover
            cls._instance = cls(*args, **kwargs)
        return cls._instance
    
    # Replace the original methods with our new ones
    cls.__init__ = __init__
    cls.instance = classmethod(instance)
    
    return cls 
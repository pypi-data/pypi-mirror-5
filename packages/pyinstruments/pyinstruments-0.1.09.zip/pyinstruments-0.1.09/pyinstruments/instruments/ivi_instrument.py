"""
sub-classes of IviInstrument can be used to wrap drivers complying to IVI
specifications.
"""

class IviInstrument:
    pass

class IntermediateCollection:
    """This class emulates (almost) all the methods available 
    for a dictionnary to access the collection in the driver
    """
    def __init__(self, driver_col, wrapper_class):
        self.driver_col = driver_col
        self.wrapper_class = wrapper_class
        self._values = dict() 
        self.parent = None
        ## returns the same element if the element was already asked for
    
    def __getitem__(self, name):
        if name in self._values:
            return self._values[name]
        else:
            self._values[name] = self.wrapper_class(self.driver_col[name])
            self._values[name].wrapper_parent = self.parent
            self._values[name].wrapper_name = name
        return self._values[name]
    
    def __iter__(self):
        for i in range(len(self)):
            name = self.driver_col.keys(i+1)
            if name in self._values:
                yield self._values[name]
            else:
                self._values[name] = self.wrapper_class(\
                                self.driver_col[name])
                self._values[name].wrapper_parent = self.parent
                self._values[name].wrapper_name = name
                yield self._values[name]

    def __len__(self):
        return len(self.driver_col)
                    

    def keys(self):
        """see dict.keys()"""
        return self.driver_col.keys()

    def values(self):
        """see dict.values()"""
        
        return [self[key] for key in self.keys()]
            
    def iteritems(self):
        """see dict.iteritems()"""
        return zip(self.keys(), self.values())
        
    def __delitem__(self):
        raise NotImplementedError(\
                "cannot delete an item from a driver collection")
        
    def __setitem__(self):
        raise NotImplementedError(\
                "cannot set an item from a driver collection")
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return str(self.keys())
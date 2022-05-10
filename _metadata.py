import pandas as pd

class SubclassedSeries(pd.Series):
    @property
    def _constructor(self):
        return SubclassedSeries

    @property
    def _constructor_expanddim(self):
        return SubclassedDataFrame
    
    _metadata = ["name", "test"]
    
    def __init__(self, data=None, index=None, name=None, test=None, **kwargs):
        super().__init__(data=data, index=index, **kwargs)
        self.name = name
        self.test = test
    
    def __setattr__(self, attr, val):
        if attr == "test":
            object.__setattr__(self, attr, val)
        else:
            super().__setattr__(attr, val)
            
    def __finalize__(self, other, method=None, **kwargs):
        """propagate metadata from other to self"""
        self = super().__finalize__(other, method=method, **kwargs)

        # merge operation: using metadata of the left object
        if method == "merge":
            for name in self._metadata:
                object.__setattr__(self, name, getattr(other.left, name, None))
        # concat operation: using metadata of the first object
        elif method == "concat":
            for name in self._metadata:
                object.__setattr__(self, name, getattr(other.objs[0], name, None))

        elif method == "unstack":
            # unstack adds multiindex columns and reshapes data.
            # it never makes sense to retain geometry column
            ...
            #self._geometry_column_name = None
            #self._crs = None
        return self
    
    def to_frame(self, name=None):
        
        test = self.test
        
        if name:
            self = self.to_frame(name=name)
        
        self.test = test
        
        return self


class SubclassedDataFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return SubclassedDataFrame

    @property
    def _constructor_sliced(self):
        return SubclassedSeries
    
    _metadata = ["test"]
    
    def __init__(self, data=None, test=None, **kwargs):
        super().__init__(data=data, **kwargs)
        self.test = test
    
    def __setattr__(self, attr, val):
        if attr == "test":
            object.__setattr__(self, attr, val)
        else:
            super().__setattr__(attr, val)
    
    def __finalize__(self, other, method=None, **kwargs):
        """propagate metadata from other to self"""
        self = super().__finalize__(other, method=method, **kwargs)

        # merge operation: using metadata of the left object
        if method == "merge":
            for name in self._metadata:
                object.__setattr__(self, name, getattr(other.left, name, None))
        # concat operation: using metadata of the first object
        elif method == "concat":
            for name in self._metadata:
                object.__setattr__(self, name, getattr(other.objs[0], name, None))

            if (self.columns == self.test).sum() > 1:
                raise ValueError(
                    "Concat operation has resulted in multiple columns using "
                    f"the geometry column name '{self._geometry_column_name}'.\n"
                    f"Please ensure this column from the first DataFrame is not "
                    f"repeated."
                )
        elif method == "unstack":
            # unstack adds multiindex columns and reshapes data.
            # it never makes sense to retain geometry column
            ...
            #self._geometry_column_name = None
            #self._crs = None
        return self


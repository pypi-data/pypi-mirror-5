class CursorProxy(object):
    
    def __init__(self, model, cursor):
        self._model = model
        self._cursor = cursor
        
        
    def __getitem__(self, index):
        return self._model(self._cursor.__getitem__(index))
        
        
    def __getattr__(self, name):
        return getattr(self._cursor, name)
        
    def __iter__(self):
        for d in self._cursor:
            yield self._model(**d)
        
    def next(self):
        if self._cursor is None:
            raise StopIteration
        return self._model(**self._cursor.next())
        
    def clone(self):
        return CursorProxy(self, self._model, self._cursor.clone())
        
    def limit(self, n):
        self._cursor.limit(n)
        return self
        
    def skip(self, n):
        self._cursor.skip(n)
        return self
        
    def sort(self, key_or_list, direction=None):
        self._cursor.sort(key_or_list, direction)
        return self
class DataBinder(object):
    def bind(self, **kwargs):
        for key in self.__dict__:
            if key in kwargs:
                self.__dict__[key] = kwargs[key]

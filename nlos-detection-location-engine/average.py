
MAX_FILTER_SIZE = 1024

class Average():

    _sum = None
    _filterLengthDefault = None
    _filterLength = None
    _filterCount = None
    _initialised = None
    _isMoving = None
    _values = []

    def __init__(self, flen):

        if flen < 1:
            flen = 1
        if flen > MAX_FILTER_SIZE:
            flen = MAX_FILTER_SIZE
            
        self._sum = 0
        self._filterLengthDefault = flen
        self._filterLength = flen
        self._filterCount = 0
        self._initialised = False
        self._isMoving = False
        self._values = []

    def process_ma(self, x):
        #TODO
        pass
    def process_me(self, x):
        
        self.__process_filter_buffer(x)

        self._sum = max = min = self._values[0]

        for element in self._values[1:]:
            if element > max:
                max = element
            if element < min:
                min = element
            self._sum += element
        
        sumfinal = self._sum - max - min

        self._filterCount = self._filterCount + 1

        if len(self._values) <= 2:
            return self._sum / len(self._values)

        return sumfinal / (len(self._values) - 2)
        
    def set_is_moving(self, moving):
        self._isMoving = moving

    def configure(self, flen):
        if flen < 1:
            flen = 1
        if flen > MAX_FILTER_SIZE:
            flen = MAX_FILTER_SIZE
        self._filterLength = flen
        self._filterCount = 0
        self._filterLengthDefault = flen

    def __process_filter_buffer(self, x):

        if self._isMoving:
            if len(self._values) >= self._filterLengthDefault:
                self._values = self._values[(-self._filterLengthDefault):]
        else:
            if len(self._values) >= MAX_FILTER_SIZE:
                self._values = self._values[(-MAX_FILTER_SIZE):]

        self._values.append(x)

def Motion_Filter_ME(average, input):

    _output = average.process_me(input)

    return _output

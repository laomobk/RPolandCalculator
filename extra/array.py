# RPolandCalculator
# standard module : array
from rpoland import (Variable, check_variable, 
                         unpack_variable, CalcException)

def get(array, index):
    #a = unpack_variable(check_variable(array))
    #i = unpack_variable(check_variable(index))

    if not hasattr(array, '__getitem__'):
        raise CalcException('E: %s is not subscriptable')

    try:
        v = array[int(index)]
    except (TypeError, IndexError) as e:
        raise CalcException('E: %s' % str(e))
    
    return unpack_variable(v)

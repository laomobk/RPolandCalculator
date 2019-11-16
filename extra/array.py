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


def pop(array, index):
    if not hasattr(array, '__getitem__'):
        raise CalcException('E: %s is not subscriptable')

    try:
        v = array.pop(int(index))
    except (TypeError, IndexError) as e:
        raise CalcException('E: %s' % str(e))
    
    return unpack_variable(v)


def remove(array, _object):
    if not hasattr(array, '__getitem__'):
        raise CalcException('E: %s is not subscriptable')

    try:
        v = array.remove(_object)
    except (TypeError, IndexError) as e:
        raise CalcException('E: %s' % str(e))
    
    return unpack_variable(None)


def insert(array, index, _object):
    if not hasattr(array, '__getitem__'):
        raise CalcException('E: %s is not subscriptable')

    try:
        v = array.insert(int(index), _object)
    except (TypeError, IndexError) as e:
        raise CalcException('E: %s' % str(e))
    
    return unpack_variable(v)


def equals(arrayA, arrayB):
    if not hasattr(arrayA, '__getitem__') or not hasattr(arrayB, '__getitem__') :
        raise CalcException('E: %s is not subscriptable')

    try:
        return unpack_variable((arrayA and arrayB))
    except (TypeError, IndexError) as e:
        raise CalcException('E: %s' % str(e))
    

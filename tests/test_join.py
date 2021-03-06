from pathos.parallel import *
from pathos.parallel import __STATE as pstate

from pathos.multiprocessing import *
from pathos.multiprocessing import __STATE as mstate

from pathos.threading import *
from pathos.threading import __STATE as tstate

from pathos.helpers import cpu_count

def squared(x):
  return x**2

def test_basic(pool, state):
    res = pool.map(squared, range(2))
    assert res == [0, 1]
    res = pool.map(squared, range(2))
    assert res == [0, 1]

    # join needs to be called after close
    try:
        pool.join()
    except AssertionError:
        pass
    else:
        raise AssertionError
    pool.close()

    # map fails when closed
    try:
        pool.map(squared, range(2))
    except AssertionError:
        pass
    else:
        raise AssertionError

    obj = pool._serve()
    assert obj in state.values()

    # serve has no effect on closed
    try:
        pool.map(squared, range(2))
    except AssertionError:
        pass
    else:
        raise AssertionError

    # once restarted, map works
    pool.restart()
    res = pool.map(squared, range(2))
    assert res == [0, 1]

    # assorted kicking of the tires...
    pool.close()
    pool.restart()
    res = pool.map(squared, range(2))
    assert res == [0, 1]
    pool.close()
    pool.join()
    pool._serve()
    try:
        pool.map(squared, range(2))
    except AssertionError:
        pass
    else:
        raise AssertionError

    pool.join()
    try:
        pool.map(squared, range(2))
    except AssertionError:
        pass
    else:
        raise AssertionError

    pool.clear()
    res = pool.map(squared, range(2))
    assert res == [0, 1]

    try:
        pool.join()
    except AssertionError:
        pass
    else:
        raise AssertionError

    pool.close()
    pool.join()
    try:
        pool.map(squared, range(2))
    except AssertionError:
        pass
    else:
        raise AssertionError
    pool.restart()
    res = pool.map(squared, range(2))
    assert res == [0, 1]
    pool.close()
    pool.join()
    try:
        pool.map(squared, range(2))
    except AssertionError:
        pass
    else:
        raise AssertionError

    pool._serve()
    try:
        pool.map(squared, range(2))
    except AssertionError:
        pass
    else:
        raise AssertionError

    pool.restart()
    res = pool.map(squared, range(2))
    assert res == [0, 1]
    pool.close()
    try:
        pool.map(squared, range(2))
    except AssertionError:
        pass
    else:
        raise AssertionError

    pool.restart()
    res = pool.map(squared, range(2))
    assert res == [0, 1]
    obj = pool._serve()
    assert obj in state.values()
    assert len(state) == 1
    pool.terminate()
    pool.clear()
    assert len(state) == 0
    return


def test_rename(pool, state):
    return


def test_nodes(pool, state):
    new_pool = type(pool)

    nodes = cpu_count()
    if nodes < 2: return
    half = nodes/2

    res = pool.map(squared, range(2))
    assert res == [0, 1]
    pool.close()

    # doesn't create a new pool... IS IT BETTER IF IT DOES?
    pool = new_pool()
    try:
        pool.map(squared, range(2))
    except AssertionError:
        pass
    else:
        raise AssertionError
    
    # creates a new pool (nodes are different)
    def nnodes(pool):
        return getattr(pool, '_'+new_pool.__name__+'__nodes')
    old_nodes = nnodes(pool)
    pool = new_pool(nodes=half)
    new_nodes = nnodes(pool)
    if isinstance(pool, ParallelPool):
        print 'SKIPPING: new_pool check for ParallelPool' #FIXME
    else:
        res = pool.map(squared, range(2))
        assert res == [0, 1]
        assert new_nodes < old_nodes

    pool.close()
    try:
        pool.map(squared, range(2))
    except AssertionError:
        pass
    else:
        raise AssertionError

    # creates a new pool (nodes are different)
    pool = new_pool()
    if isinstance(pool, ParallelPool):
        print 'SKIPPING: new_pool check for ParallelPool' #FIXME
    else:
        res = pool.map(squared, range(2))
        assert res == [0, 1]
    pool.close()
    # doesn't create a new pool... IS IT BETTER IF IT DOES?
    pool = new_pool()
    try:
        pool.map(squared, range(2))
    except AssertionError:
        pass
    else:
        raise AssertionError

    assert len(state) == 1
    pool.clear()
    assert len(state) == 0
    pool = new_pool()
    res = pool.map(squared, range(2))
    assert res == [0, 1]
    assert len(state) == 1
    pool.terminate()
    assert len(state) == 1
    pool.clear()
    assert len(state) == 0
    return


def test_rename(pool, state):
    new_pool = type(pool)
    res = pool.map(squared, range(2))
    assert res == [0, 1]
    old_id = pool._id

    # change the 'id'
    pool._id = 'foobar'
    pool = new_pool() # blow away the 'id' change
    res = pool.map(squared, range(2))
    assert res == [0, 1]
    assert len(state) == 1
    assert 'foobar' not in state.keys()

    # change the 'id', but don't re-init
    pool._id = 'foobar'
    res = pool.map(squared, range(2))
    assert res == [0, 1]
    assert len(state) == 2
    assert 'foobar' in state.keys()

    pool.close()     
    try:
        pool.map(squared, range(2))
    except AssertionError:
        pass
    else:
        raise AssertionError
    pool.terminate()
    assert len(state) == 2
    assert 'foobar' in state.keys()
    pool.clear()
    assert len(state) == 1
    assert 'foobar' not in state.keys()

    pool._id = old_id
    res = pool.map(squared, range(2))
    assert res == [0, 1]
    pool.terminate()
    pool.clear()
    assert len(state) == 0
    return


if __name__ == '__main__':
    from pathos.helpers import freeze_support
    freeze_support()

    test_basic(ThreadPool(), tstate)
#   test_basic(ProcessPool(), mstate)
#   test_basic(ParallelPool(), pstate)

    test_rename(ThreadPool(), tstate)
    test_rename(ProcessPool(), mstate)
    test_rename(ParallelPool(), pstate)

    test_nodes(ThreadPool(), tstate)
    test_nodes(ProcessPool(), mstate)
    test_nodes(ParallelPool(), pstate)


# EOF

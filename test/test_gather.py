import txaio

from util import await


def test_gather_two():
    '''
    Wait for two Futures.
    '''

    errors = []
    results = []
    calls = []

    def foo():
        def codependant(*args, **kw):
            calls.append((args, kw))
            return 42
        return txaio.as_future(codependant)

    def method(*args, **kw):
        calls.append((args, kw))
        return "OHAI"
    f0 = txaio.as_future(method, 1, 2, 3, key='word')
    f1 = txaio.as_future(foo)

    f2 = txaio.gather([f0, f1])

    def done(arg):
        results.append(arg)

    def error(fail):
        errors.append(fail)
        # fail.printTraceback()
    txaio.add_callbacks(f2, done, error)

    await(f0)
    await(f1)
    await(f2)

    assert len(results) == 1
    assert len(errors) == 0
    assert results[0] == ['OHAI', 42] or results[0] == [42, 'OHAI']
    assert len(calls) == 2
    assert calls[0] == ((1, 2, 3), dict(key='word'))
    assert calls[1] == (tuple(), dict())


def test_gather_no_consume():
    '''
    consume_exceptions=False
    '''

    errors = []
    results = []
    calls = []

    f0 = txaio.create_future_error(error=RuntimeError("f0 failed"))
    f1 = txaio.create_future_error(error=RuntimeError("f1 failed"))

    f2 = txaio.gather([f0, f1], consume_exceptions=False)

    def done(arg):
        results.append(arg)

    def error(fail):
        errors.append(fail)
        # fail.printTraceback()
    txaio.add_callbacks(f0, done, error)
    txaio.add_callbacks(f1, done, error)
    txaio.add_callbacks(f2, done, error)

    # FIXME more testing annoyance; the propogated errors are raise
    # out of "run_until_complete()" as well; fix util.py
    for f in [f0, f1, f2]:
        try:
            await(f)
        except:
            pass

    assert len(results) == 0
    assert len(errors) == 3
    assert len(calls) == 0
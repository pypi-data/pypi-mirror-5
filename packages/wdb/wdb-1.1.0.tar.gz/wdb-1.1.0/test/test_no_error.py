# *-* coding: utf-8 *-*
from .conftest import use


@use('error_ignored_in_script.py')
def test_with_error_ignored(socket):
    # If it doesn't timeout this is good
    socket.join()


@use('error_not_ignored_in_script.py')
def test_with_error_not_ignored_because_of_full(socket):
    socket.start()
    assert socket.receive().command == 'Init'
    assert socket.receive().command == 'Title'
    trace = socket.receive()
    assert trace.command == 'Trace'
    assert trace.data.trace[-1].current == True
    assert socket.receive().command == 'SelectCheck'
    assert socket.receive().command == 'Echo'
    assert socket.receive().command == 'Watched'
    socket.send('Continue')

    assert socket.receive().command == 'Title'
    trace = socket.receive()
    assert trace.command == 'Trace'
    assert trace.data.trace[-1].current == False
    assert socket.receive().command == 'SelectCheck'
    assert socket.receive().command == 'Watched'
    socket.send('Continue')

    socket.join()

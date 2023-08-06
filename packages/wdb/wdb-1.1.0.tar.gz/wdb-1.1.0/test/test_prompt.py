# *-* coding: utf-8 *-*
from .conftest import use, u


@use('movement.py')
def test_eval(socket):
    socket.start()
    socket.assert_init()
    socket.send('Next')
    socket.assert_position(line=12)
    socket.send('Eval', 'l')
    print_msg = socket.receive()
    assert print_msg.command == 'Print'
    assert print_msg.data['for'] == 'l'
    assert print_msg.data.result == '[]'
    watched_msg = socket.receive()
    assert watched_msg.command == 'Watched'

    socket.send('Next')
    socket.assert_position(line=13)

    socket.send('Eval', 'l')
    print_msg = socket.receive()
    assert print_msg.command == 'Print'
    assert print_msg.data['for'] == 'l'
    assert 'class="inspect">3</a>]' in print_msg.data.result

    watched_msg = socket.receive()
    assert watched_msg.command == 'Watched'

    socket.send('Eval', 'l = None')
    print_msg = socket.receive()
    assert print_msg.command == 'Print'

    assert print_msg.data['for'] == u('l = None')
    assert print_msg.data.result == ''

    watched_msg = socket.receive()
    assert watched_msg.command == 'Watched'

    socket.send('Continue')
    socket.join()


@use('movement.py')
def test_eval(socket):
    socket.start()
    socket.assert_init()
    socket.send('Next')
    socket.assert_position(line=12)
    socket.send('Next')
    socket.assert_position(line=13)

    socket.send('Dump', 'l')
    print_msg = socket.receive()
    assert print_msg.command == 'Dump'
    assert print_msg.data['for'] == u('l ⟶ [3] ')
    assert print_msg.data.val

    socket.send('Continue')
    socket.join()

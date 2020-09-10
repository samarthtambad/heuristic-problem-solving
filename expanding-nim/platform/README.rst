Expanding Nim
=============

Basics
------

This repository contains code for a platform to run the Expanding Nim game. It consists
of a game manager, a server and a client, along with some scripts to control the server
and the client.

Rules
-----

First, the game is started by providing an initial number of stones, *n*, and the number of
resets, *r*, available to each player. The game begins once both clients have connected to
the server. The first player can take a maximum of *m* stones, which is 3 by default but
can be configured at time of starting the game. After that, the players take turn to remove
stones and the player who removes the last stone win. The maximum number of stones that can
be remove in each move is 1 + the previous maximum. However, if a player chooses to use the
reset option, this number gets reset to the initial maximum, *m*. If a player moves out of
turn, tries to use more than *r* resets, tries to take more than stones than the current
maximum or times out the game is automatically awarded to the other player.

Classes
-------

Client
++++++

The ``Client`` class in the ``client`` module should be instantiated for each player. The
class provides two primary methods for communicating with the game ``make_move`` and
``receive_move``. To use the client, create an instance of the class in your Python code,
and when you have to make a move, call ``client.make_move(num_stones, reset)`` and to get
the opponents move after that call ``client.receive_move()``. Both these functions will
return the state of the game after the move is made as a dict. See the docstrings of these
functions for the exact keys. Also, see ``sample_client_usage.py`` for some boiler plate
code to interact with the client.

Besides these two methods, there are also ``send_move`` and ``get_move`` which are wrappers
around the two former methods to allow printing to standard out and using the client through
a different language. To use the client through these methods, run the ``exp-nim`` script
using a named pipe to your program, or run the script as a subprocess of your program with
stdout and stdin piped into you program. See the Scripts section below or the docstring of
the script for details. Note that you will have to do some parsing if you use this method.

Game state
**********

On initializtion, the number of stones will be available as ``client.init_stones`` and
number of resets will be available as ``client.init_resets``. These are just the values
at start of the game and don't change later.

The game state is returned after by both the ``make_move`` and ``receive_move`` methods.
The state is returned as a dict with the below keys:

.. code-block::

    {
        'finished': A boolean indicator whether the game finished
        'reason': What caused the game to finish if it did
        'winner': Who won the game if it finished
        'current_max': The max number of stones that can be removed in the next turn
        'stones_left': Total stones left
        'stones_removed': Stones removed in the previous turn
        'reset_used': A boolean indicator whether reset was used in the previous turn
    }


Writing your own client
***********************

If you wish to implement your own client in another language, you need to implement the
below methods in the client.

``Constructor``:

The constructor should create a socket and be able to connect that socket to the server
socket using IP address and port number. On connecting with the server socket, the client
should then send a JSON containing the keys ``name``, which is a string and ``order``, which
is 0 if the client belongs to the first player, and 1 if it belongs to the second player. After
that, the client should receive data from the server. The server will send a JSON containing
the keys ``init_stones`` and ``init_resets``, which are the initial number of stones and the
number of resets available.

``make_move`` method equivalent:

This method should send a JSON to the server containing the keys ``num_stones``, which are
the number of stones to remove and ``reset``, which is a boolean indicator for whether you
want to reset the current max for the next turn. If the client belongs to the player moving
first, this method should also be called immediately after the constructor. All other keys
in the JSON will be ignored. The server will return a JSON containing the game state as
described above.

``receive_move`` method equivalent:

This method should be called immediately after calling the ``make_move`` equivalent in your
client. Again, the server will return the game state after the opponent's client has made
a move. Do no pass any data to the server in this method, otherwise it will deadlock.

Your script or ``main`` method should then call the ``make_move`` and ``receive_move``
equivalent methods repeatedly and check if the game ended after each move by looking at the
``finished`` value in the JSON that is returned by the server. See ``sample_client_usage.py``
script for a working example.

ExpVimManager
+++++++++++++

This is the class that contains the rules of the game and controls it. It is initialized
only once for each game, which can be done using the ``start-game.py`` script. The script
provides various options to control the rules of the game. See the script documentation
for details on how to start the game.

Server
++++++

This class should only be instantiated through the ``ExpNimManager`` class and is not
relevant to the game by itself. You can ignore this unless you find a bug in it.

Scripts
-------

exp-nim
+++++++

This script is a command-line interface to the game and can be used interactively or can be
used as a client wrapper. This script can be run as:

``./exp-nim [-f] -n <name> IP:port``

where:

| ``IP`` is the IP address of the server
| ``port`` is the port of the server
| ``-f`` should be set if you are the first player
| ``-n`` is a name of your choice


You can also automate the game by piping a list of moves into the script:

``move-list | exp-nim [-f] -n <name> IP:port``

For scripting the game (on Linux), you can create a named pipe and use that:

| ``mkfifo cmd-pipe``
| ``./sample-script.exp < cmd-pipe | ./exp-nim [-f] -n <name> IP:port > cmd-pipe``

The move is entered in the format ``%d %d`` where the first input is the number
of stones to remove and reset indicates that you want to reset the current max.
Reset will be interpreted as a boolean using Python's bool() function.

If you have ``expect`` installed on your machine, you can try running this with
the provided ``sample-script.exp``.

start-game.py
+++++++++++++

Run this script with the following options to start the server:

``./start-game.py [-m <max>|-a <address>|-p <port>|-t <secs>] n r``

where:

| ``n`` is the number of stones to start game with
| ``r`` is the number of resets available to the players
| ``-m`` is the initial maximum number (Default: 3)
| ``-a`` is the IP address to listen on (Default: all)
| ``-p`` is the port to run server on (Default: 9000)
| ``-t`` is the game time in seconds (Default: 120)

Misc
----

You can tail the game as it progresses by tailing the ``game-log.txt`` file created
during the game. This can be used for debugging or just to enjoy the game.

In case of any issues or bugs, please email me at Munir Contractor <mmc691@nyu.edu>.

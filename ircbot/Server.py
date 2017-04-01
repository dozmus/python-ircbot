from threading import Thread

from ircbot.IrcSocket import IrcSocket


class Server(object):

    def __init__(self, server_details, user, channels):
        self.thread = Thread(target=self.run)
        self.server_details = server_details
        self.user = user
        self.channels = channels
        self.running = False

    def start(self):
        self.thread.start()
        pass

    def request_stop(self):
        self.running = False
        pass

    def run(self):
        self.running = True
        init_required = True

        # Connect to server
        print('Connecting to server...')
        socket = IrcSocket(self.server_details)

        # Read loop
        while self.running:  # TODO handle disconnects
            lines = socket.read_lines()

            if init_required:
                # Initialise connection
                print('Initialising connection')
                socket.init(self.user)
                init_required = False

            for line in lines:
                if line.startswith('PING'):
                    socket.pong(line)

                print('> %s' % line)

        print('Closing connection...')
        socket.close()

# Application entry-point
if __name__ == "__main__":
    # Connect to server
    user = {'nickname': 'PyBot3092', 'username': 'PyBot3092', 'realname': 'A Python IRC bot.', 'password': None}
    server_details = {'hostname': 'irc.rizon.net', 'port': 6697, 'ssl': True}
    channels = {'#dictated.java': ''}

    server = Server(server_details, user, channels)
    server.start()

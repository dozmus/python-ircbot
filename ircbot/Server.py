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
                # Ping-Pong
                if line.startswith('PING'):
                    socket.pong(line)
                    continue

                # Parse message
                msg = parse(line)

                # On-connect
                if msg['command'] == '001':
                    print('Joining default channels')

                    for channel, password in self.channels.items():
                        socket.join_channel(channel, password)

                # Other
                print(line)

        print('Closing connection...')
        socket.close()


def parse(line):
    line = line[1:] if line.startswith(':') else line
    colon_idx = line.find(' :')

    if colon_idx is not -1:
        msg_info = line[:colon_idx].split(' ')
        msg_data = line[colon_idx + 2:]
    else:
        msg_info = line.split(' ')
        msg_data = ''

    return {
        'server': msg_info[0],
        'command': msg_info[1],
        'target': msg_info[2] if len(msg_info) >= 3 else None,
        'args': msg_info[3:] if len(msg_info) >= 4 else None,
        'msg': msg_data
    }

# Application entry-point
if __name__ == "__main__":
    # Connect to server
    user = {'nickname': 'PyBot3092', 'username': 'PyBot3092', 'realname': 'A Python IRC bot.', 'password': None}
    server_details = {'hostname': 'irc.rizon.net', 'port': 6697, 'ssl': True}
    channels = {'#dictated.java': ''}

    server = Server(server_details, user, channels)
    server.start()

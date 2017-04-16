from platform import python_version
from platform import system

from threading import Thread

from ircbot.IrcSocket import IrcSocket


class IrcClient(object):
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

                # Print line
                print(line)

                # Parse message
                irc_msg = parse(line)

                # On-connect
                if irc_msg['command'] == '001':
                    print('Joining default channels')

                    for channel, password in self.channels.items():
                        socket.join_channel(channel, password)

                # CTCP VERSION reply
                if irc_msg['target'] == self.user['nickname'] and irc_msg['msg'] == 'VERSION':
                    print('Replying to CTCP VERSION from ' + irc_msg['source']['sender'])

                    if irc_msg['command'] == 'NOTICE':
                        socket.notice(irc_msg['source']['nickname'], version_response())
                    elif irc_msg['command'] == 'PRIVMSG':
                        socket.privmsg(irc_msg['source']['nickname'], version_response())

        print('Closing connection...')
        socket.close()


def version_response():
    """ Return the version text which is used to respond to CTCP VERSION requests. """
    return 'VERSION irc-bot 1.0.0 / Python {} on {}'.format(python_version(), system())


def parse(line):
    line = line[1:] if line.startswith(':') else line
    colon_idx = line.find(' :')

    # Parse general structure
    if colon_idx is not -1:
        msg_info = line[:colon_idx].split(' ')
        msg_data = line[colon_idx + 2:]
    else:
        msg_info = line.split(' ')
        msg_data = ''

    # Parse sender
    source_details = {'sender': msg_info[0]}

    if '!' in msg_info[0] and '@' in msg_info[0]:
        excl_idx = msg_info[0].find('!')
        at_idx = msg_info[0].find('@')

        source_details['nickname'] = msg_info[0][:excl_idx]
        source_details['username'] = msg_info[0][excl_idx + 1:at_idx]
        source_details['hostname'] = msg_info[0][at_idx + 1:]

    return {
        'source': source_details,
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

    client = IrcClient(server_details, user, channels)
    client.start()

import socket
import ssl


class IrcSocket(object):

    def __init__(self, server_details):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_details['hostname'], server_details['port']))
        self.line_buffer = ''

        if server_details['ssl']:
            self.socket = ssl.wrap_socket(self.socket)

    def close(self):
        self.socket.close()

    def init(self, user):
        if user['password'] is not None:
            self.write_line('/NICKSERV IDENTITY {}'.format(user['password']))  # TODO allow this to be set

        self.nick(user['nickname'])
        self.user(user['username'], user['realname'])

    def nick(self, nickname):
        self.write_line('NICK {}'.format(nickname))

    def user(self, username, realname, mode=8):
        self.write_line('USER {} {} * :{}'.format(username, mode, realname))

    def join_channel(self, channel, password=None):
        if password is None or len(password) == 0:
            self.write_line('JOIN {}'.format(channel))
        else:
            self.write_line('JOIN {} {}'.format(channel, password))

    def part_channel(self, channel):
        self.write_line('PART {}'.format(channel))

    def notice(self, target, message):
        # TODO handle overflow
        self.write_line('NOTICE {} :{}'.format(target, message))

    def privmsg(self, target, message):
        # TODO handle overflow
        self.write_line('PRIVMSG {} :{}'.format(target, message))

    def pong(self, line):
        """ Replaces the first four characters of the line with 'PONG' and writes it to the socket. """
        self.write_line('PONG {}'.format(line[4:]))
        pass

    def write_line(self, line):
        """ Writes the line to the socket followed by carriage return and new line. It will omit any characters
        after 510 characters.
        
        """
        # TODO check if socket is open?
        # TODO create a queued writer, to throttle output
        self.socket.send('{}\r\n'.format(line[:510]).encode('UTF-8'))

    def read_lines(self, max_loops=10):
        # Reading buffer
        lines = []
        self.line_buffer += self.socket.recv(512).decode('UTF-8')

        # Looping until we are out of lines to parse
        for i in range(0, max_loops):
            # Finding the line break, if one is missing we stop
            line_break_index = self.line_buffer.find('\r\n')

            if line_break_index == -1:
                break

            # Parsing the current line and adding it to our current list
            line = self.line_buffer[:line_break_index]
            self.line_buffer = self.line_buffer[line_break_index + 2:]
            lines.append(line)

        # Returning the parsed lines this receive
        return lines

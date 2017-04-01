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
        if user.password is not None:
            self.write_line('/NICKSERV IDENTITY {}'.format(user.password))  # TODO allow this to be set

        self.nick(user.nickname)
        self.user(user.username, user.realname)

    def nick(self, nickname):
        self.write_line('NICK {}'.format(nickname))

    def user(self, username, realname, mode=8):
        self.write_line('USER {} {} * :{}'.format(username, mode, realname))

    def join_channel(self, channel):
        self.write_line('JOIN {}'.format(channel))

    def part_channel(self, channel):
        self.write_line('PART {}'.format(channel))

    def notice(self, target, message):
        self.write_line('NOTICE {} :{}'.format(target, message))

    def privmsg(self, target, message):
        self.write_line('PRIVMSG {} :{}'.format(target, message))

    def write_line(self, line):
        # TODO check if socket is open?
        # TODO create a queued writer, to throttle output
        # TODO limit line to 510 chars, handle overflow, etc.
        # self.socket.send(bytes('{}\r\n'.format(line), 'UTF-8'))
        self.socket.send('{}\r\n'.format(line).encode('UTF-8'))

    def read_lines(self):
        # Reading buffer
        lines = []
        self.line_buffer += self.socket.recv(512).decode('UTF-8')

        # Looping until we are out of lines to parse
        while True:  # TODO limit to N per iteration?
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

use strict;
use warnings;
use JSON;
use IO::Socket::INET;
use Net::WebSocket::Server;
use URI::Escape;
use DBI;
use Data::Dumper;

my $host = 'localhost';
my $port = '3306';
my $database = 'chatapp';
my $username = 'duck';
my $db_password = 'Welcome@123';

my $dsn = "DBI:mysql:database=$database;host=$host;port=$port";
my $dbh = DBI->connect($dsn, $username, $db_password, { RaiseError => 1, AutoCommit => 1 }) or die "Couldn't connect to database: " . DBI->errstr;

my %user_to_connection; # This hash will store user email to WebSocket connection mapping

my $server = Net::WebSocket::Server->new(
    listen => 8080,
    on_connect => sub {
        my ($serv, $conn) = @_;
        my $remote_address = $conn->socket->peerhost . ":" . $conn->socket->peerport;
        print "Connection from $remote_address\n";
        $conn->{remote_address} = $remote_address;

        $conn->on(
            utf8 => sub {
                my ($conn, $msg) = @_;
                my $data = eval { decode_json($msg) }; # Use eval to handle possible JSON decoding errors

                if ($@) {
                    warn "Error decoding JSON: $@";
                    return;
                }

                if ($data->{type} eq 'login') {
                    my $user_email = $data->{email};
                    if (defined $user_email) {
                        $user_to_connection{$user_email} = $conn;
                        print "User logged in: $user_email\n";
                    } else {
                        print "Error: No email provided in login message.\n";
                    }
                } elsif ($data->{type} eq 'message') {
                    my $sender = $data->{sender_id};
                    my $receiver = $data->{receiver_id};

                                        warn "Received message from sender: $sender, to receiver: $receiver\n";

                    warn "####### WebSocket server: sender #####".Dumper($sender);
                    warn "####### WebSocket server: receiver #####".Dumper($receiver);
                    warn "####### WebSocket server: data #####".Dumper($data);

                    if (defined $receiver) {
                        my $message = {
                            type => 'message',
                            sender_id => $sender,
                            content => $data->{content},
                            time => $data->{time},
                            receiver_id => $receiver, # Use $receiver directly
                        };

                        # Save message to database
                        my $sth = $dbh->prepare("INSERT INTO chat_history (sender, receiver, content) VALUES (?, ?, ?)");
                        $sth->execute($sender, $receiver, $data->{content});

                        send_message($message);
                                                warn "Sent message to receiver: $receiver\n";
                        warn "####### WebSocket server: MESSAGE #####".Dumper($message);

                        if (exists $user_to_connection{$receiver}) {
                            my $receiver_conn = $user_to_connection{$receiver};
                            $receiver_conn->send_utf8(encode_json($message));
                            print "Message sent to $receiver\n";
                        } else {
                            print "Receiver $receiver not connected\n";
                            # Handle if receiver is not connected
                        }
                    } else {
                        print "Error: No receiver specified in message.\n";
                    }
                }
            },
            disconnect => sub {
                my ($conn, $code, $reason) = @_;
                my $user_email;
                # Find and remove the disconnected user from %user_to_connection
                foreach my $email (keys %user_to_connection) {
                    if ($user_to_connection{$email} == $conn) {
                        $user_email = $email;
                        last;
                    }
                }
                if ($user_email) {
                    delete $user_to_connection{$user_email};
                    print "User disconnected: $user_email\n";
                } else {
                    print "Error: User not found for disconnection.\n";
                }
            }
        );
    },
);

sub send_message {
    my ($data) = @_;

    my $receiver_email = $data->{receiver_id};

    warn "####### WebSocket server: Send Message receiver_email #####".Dumper($receiver_email);
    warn "####### WebSocket server: Send Message data #####".Dumper($data);

    if (defined $receiver_email && exists $user_to_connection{$receiver_email}) {
        my $receiver_conn = $user_to_connection{$receiver_email};
        $receiver_conn->send_utf8(encode_json($data));
    } else {
        warn "Receiver connection not found for user: $receiver_email\n";
    }
}

# Handle server startup error
eval {
    $server->start;
};
if ($@) {
    die "Error starting server: $@\n";
}
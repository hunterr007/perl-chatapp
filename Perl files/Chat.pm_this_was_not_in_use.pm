package Chat;

use strict;
use warnings;
use DBI;
use JSON::XS;

my $host = 'localhost';
my $port = '3306';
my $database = 'chatapp';
my $username = 'duck';
my $password = 'Welcome@123';

my $dsn = "DBI:mysql:database=$database;host=$host;port=$port";
my $dbh = DBI->connect($dsn, $username, $password,{ RaiseError => 1, AutoCommit => 1 }) or die "Couldn't connect to database: " . DBI->errstr;

sub get_chat_interface {
return <<HTML;
                <!-- Right pane: Chat interface -->
                    <div id="chat-interface">
                            <!-- Display user name -->
                                    <div id="user-name"></div>

                                            <!-- Display chat history -->
                                                    <div id="chat-history"></div>

                                                            <!-- Message input -->
                                                                    <input type="text" id="message-input">
                                                                            <button onclick="sendMessage()">Send</button>
                                                                                </div>
HTML
                                                                        }

                                                                        sub send_message {
                                                                                    my ($sender, $receiver, $message) = @_;

                                                                                        my $sth = $dbh->prepare("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)");
                                                                                            $sth->execute($sender, $receiver, $message);
                                                                                    }

                                                                                    sub handle_message {
                                                                                                my ($conn, $message) = @_;

                                                                                                    my $decoded_message = decode_json($message);
                                                                                                        my $sender = $decoded_message->{sender};
                                                                                                            my $receiver = $decoded_message->{receiver};
                                                                                                                my $message_text = $decoded_message->{message};

                                                                                                                    my $sth = $dbh->prepare("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)");
                                                                                                                       $sth->execute($sender, $receiver, $message_text);

                                                                                                                           my $broadcast_message = {

    sender => $sender,

            message => $message_text

                };

                    my $json_message = encode_json($broadcast_message);

                        $server->broadcast_utf8($json_message);

                }


                1;
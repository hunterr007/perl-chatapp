#!/usr/bin/perl
use strict;
use warnings;
use AnyEvent;
use AnyEvent::Socket;
use AnyEvent::WebSocket::Server;
use DBI;
use JSON;

my $server = AnyEvent::WebSocket::Server->new;
my %clients;
my $host = 'localhost';
my $port = '3306';
my $database = 'chatapp';
my $username = 'duck';
my $password = 'Welcome@123';

my $dsn = "DBI:mysql:database=$database;host=$host;port=$port";
my $dbh = DBI->connect($dsn, $username, $password,{ RaiseError => 1, AutoCommit => 1 }) or die "Couldn't connect to database: " . DBI->errstr;

tcp_server undef, 8081, sub {
        my ($fh) = @_;
        $server->establish($fh)->cb(sub {
                        my $conn = eval { shift->recv };
                        return unless $conn;

                        my $id = fileno($fh);
                        $clients{$id} = $conn;

                        $conn->on(each_message => sub {
                                        my ($conn, $msg) = @_;
                                        my $data = decode_json($msg->body);

                                        my $sender_id = $data->{sender_id};
                                        my $receiver_id = $data->{receiver_id};
                                        my $message = $data->{message};


                                        $dbh->do("INSERT INTO chats (sender_id, receiver_id, message) VALUES (?, ?, ?)",
                                                undef, $sender_id, $receiver_id, $message);


                                        my $receiver_conn = $clients{$receiver_id};
                                        if ($receiver_conn) {
                                                $receiver_conn->send($msg->body);
                                        }
                                });

                        $conn->on(finish => sub {
                                        delete $clients{$id};
                                });
                });
};

print "WebSocket server running on ws://localhost:8081\n";
AnyEvent->condvar->recv;
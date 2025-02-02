#!/usr/bin/perl
use strict;
use warnings;
use Net::WebSocket::Server;

my %connections;

my $server = Net::WebSocket::Server->new(
            listen => 3000,
                on_connect => sub {
                                my ($serv, $conn) = @_;


                                        $connections{$conn} = $conn;

                                                print "Client connected\n";

                                                        $conn->on(
                                                                            utf8 => sub {
                                                                                                    my ($conn, $msg) = @_;
                                                                                                                    print "Message received: $msg\n";


                                                                                                                                    foreach my $client (keys %connections) {

                        $connections{$client}->send_utf8($msg) unless $client == $conn;

                                        }

                                                    },

                                                                disconnect => sub {

                                                                                        my ($conn, $code, $reason) = @_;

                                                                                                        delete $connections{$conn};

                                                                                                                        print "Client disconnected\n";

                                                                                                                                   },

                                                                                                                                                                                       );


        },


);



$server->start;
#!/usr/bin/perl
use strict;
use warnings;
use CGI;
use JSON::XS;
use lib '../lib';
use Chat;

my $cgi = CGI->new;
print $cgi->header('text/html');


if ($cgi->param('action') eq 'chat_interface') {
    my $html = Chat::get_chat_interface();
    print $html;
}


elsif ($cgi->param('action') eq 'send_message') {
    my $sender = $cgi->param('sender');
    my $receiver = $cgi->param('receiver');
    my $message = $cgi->param('message');

    Chat::send_message($sender, $receiver, $message);
    print "Message sent successfully!";
}
#!/usr/bin/perl

use strict;
use warnings;
use CGI;
use JSON;
use DBI;
use Data::Dumper;

# Initialize CGI object and print header
my $cgi = CGI->new;
print $cgi->header('application/json');

# Database connection parameters
my $host = 'localhost';
my $port = '3306';
my $database = 'chatapp';
my $db_username = 'duck';
my $db_password = 'Welcome@123';

# Establish database connection
my $dsn = "DBI:mysql:database=$database;host=$host;port=$port";
my $dbh = DBI->connect($dsn, $db_username, $db_password, {
    RaiseError => 1,
    AutoCommit => 1,
    FetchHashKeyName => 'NAME_lc'
}) or die "Couldn't connect to database: " . DBI->errstr;

# Handle incoming POST request to save message
if ($cgi->request_method() eq 'POST') {
    my $sender_id   = $cgi->param('sender_id');
    my $receiver_id = $cgi->param('receiver_id');
    my $message     = $cgi->param('message');

    # Save message to database
    my $insert_message = $dbh->prepare("
        INSERT INTO chat_history (sender, receiver, content, time)
        VALUES (?, ?, ?, NOW())
    ");
    $insert_message->execute($sender_id, $receiver_id, $message);

    # Retrieve sender's name for response
    my $get_sender_name = $dbh->prepare("
        SELECT name FROM chatusers WHERE id = ?
    ");
    $get_sender_name->execute($sender_id);
    my ($sender_name) = $get_sender_name->fetchrow_array();

    # Construct message response
    my %message_response = (
        sender_id   => $sender_id,
        sender_name => $sender_name,
        receiver_id => $receiver_id,
        content     => $message,
        time        => localtime(),
    );

    print encode_json(\%message_response);
}
# Handle GET request to fetch chat history
elsif ($cgi->request_method() eq 'GET') {
    my $sender_id   = $cgi->param('sender_id');
    my $receiver_id = $cgi->param('receiver_id');

        warn"#### Chat_message get method senderid ########".Dumper($sender_id);
        warn"#### Chat_message get method receiver_id ########".Dumper($receiver_id);

    # Fetch chat history from database
    my $get_messages = $dbh->prepare("
        SELECT ch.sender, ch.receiver, ch.content, ch.time, cu.name AS sender_name
        FROM chat_history ch
        INNER JOIN chatusers cu ON ch.sender = cu.emailaddress
        WHERE (ch.sender = ? AND ch.receiver = ?)
           OR (ch.sender = ? AND ch.receiver = ?)
        ORDER BY ch.time
    ");
    $get_messages->execute($sender_id, $receiver_id, $receiver_id, $sender_id);

    my @messages;
    while (my $row = $get_messages->fetchrow_hashref()) {
        my %message = (
            sender_id   => $row->{sender},
            sender_name => $row->{sender_name},
            receiver_id => $row->{receiver},
            content     => $row->{content},
            time        => $row->{time},
        );
        push @messages, \%message;
    }

        warn"## Chat_message get method message ####".Dumper(\@messages);

    print encode_json(\@messages);
}

# Disconnect database connection
$dbh->disconnect();
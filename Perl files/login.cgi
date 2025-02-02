#!/usr/bin/perl
use strict;
use warnings;
use lib '/usr/local/lib/site_perl';
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use DBI;
use JSON;

my $cgi = CGI->new;
print $cgi->header('application/json');

my $username = $cgi->param('username');
my $password = $cgi->param('password');

my $host = 'localhost';
my $port = '3306';
my $database = 'chatapp';
my $db_username = 'duck';
my $db_password = 'Welcome@123';

my $dsn = "DBI:mysql:database=$database;host=$host;port=$port";
my $dbh = DBI->connect($dsn, $db_username, $db_password, { RaiseError => 1, AutoCommit => 1 }) or die encode_json({ success => 0, message => "Couldn't connect to database: " . DBI->errstr });

my $sth_check = $dbh->prepare("SELECT * FROM chatusers WHERE emailaddress = ?");
$sth_check->execute($username);

if (my $user = $sth_check->fetchrow_hashref) {
    my $stored_password = $user->{password};

    if ($password eq $stored_password) {
            # print encode_json({ success => 1, message => 'Login successful.', redirect_url => "http://localhost/index.html?username=" . $cgi->escape($username) });
            print encode_json({ success => 1, message => 'Login successful.'});
    } else {
        print encode_json({ success => 0, message => 'Invalid username or password.' });
    }
} else {
    print encode_json({ success => 0, message => 'Invalid username or password.' });
}

$sth_check->finish;
$dbh->disconnect;
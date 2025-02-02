#!/usr/bin/perl

use strict;
use warnings;
use CGI;
use JSON;
use DBI;

my $host = 'localhost';
my $port = '3306';
my $database = 'chatapp';
my $username = 'duck';
my $db_password = 'Welcome@123';

my $dsn = "DBI:mysql:database=$database;host=$host;port=$port";
my $dbh = DBI->connect($dsn, $username, $db_password, { RaiseError => 1, AutoCommit => 1 }) or die "Couldn't connect to database: " . DBI->errstr;

# Create CGI object
my $cgi = CGI->new;

# Set response content type
print $cgi->header('application/json');

# Fetch users from the database
my $sql = "SELECT id, name AS username,emailaddress AS email,phonenum FROM chatusers";
my $sth = $dbh->prepare($sql);
$sth->execute;

# Fetch all rows into an array of hashes
my @users;
while (my $row = $sth->fetchrow_hashref) {
    push @users, $row;
}

# Output JSON response
print encode_json(\@users);

# Disconnect from the database
$dbh->disconnect;
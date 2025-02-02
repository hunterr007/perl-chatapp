#!/usr/bin/perl
use strict;
use warnings;
use CGI;
use JSON;
use DBI;
use Data::Dumper;

my $cgi = CGI->new;
print $cgi->header('application/json');

my $host = 'localhost';
my $port = '3306';
my $database = 'chatapp';
my $username = 'duck';
my $password = 'Welcome@123';

my $dsn = "DBI:mysql:database=$database;host=$host;port=$port";
my $dbh = DBI->connect($dsn, $username, $password,{ RaiseError => 1, AutoCommit => 1 }) or die "Couldn't connect to database: " . DBI->errstr;

if (!$dbh) {
            die "Database connection error: " . $DBI::errstr;
    }


    my $sth = $dbh->prepare("SELECT name FROM chatapp.users");
    $sth->execute();

    my @users;
    while (my $row = $sth->fetchrow_hashref) {
                push @users, $row->{name};
        }

        warn"######## USERS ########".Dumper(\@users);

        if (@users == 0) {
                    print encode_json({error => "No users found in database"});
                        exit;
                }


                print encode_json(\@users);
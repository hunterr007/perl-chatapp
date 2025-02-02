#!/usr/bin/perl
use strict;
use warnings;
use CGI;
use DBI;
use JSON;

my $cgi = CGI->new;
print $cgi->header('application/json');

my $name = $cgi->param('name');
my $emailaddress = $cgi->param('emailaddress');
my $password = $cgi->param('password');
my $phone = $cgi->param('phone');
my $confirm_password = $cgi->param('confirmPassword');

# Validation messages
my @errors;

# Validate name
unless ($name =~ /^[A-Za-z][A-Za-z ]*$/) {
    push @errors, "Name should contain only alphabets and spaces, and should not start with a space.";
}

# Validate phone number
unless ($phone =~ /^\d{10}$/) {
    push @errors, "Phone number should be numeric and 10 digits long.";
}

# Validate email address
unless ($emailaddress =~ /^[^\s@]+@[^\s@]+\.[^\s@]+$/) {
    push @errors, "Invalid email address format.";
}

# Validate password
unless ($password =~ /^(?=.*\d.*\d).{8,}$/) {
    push @errors, "Password must be at least 8 characters long and contain at least 2 numbers.";
}

# Validate confirm password
if ($password ne $confirm_password) {
    push @errors, "Passwords do not match.";
}

# If there are validation errors, return them
if (@errors) {
    my $response = {
        success => 0,
        message => join('<br>', @errors),
    };
    print encode_json($response);
    exit;
}

# Database connection details
my $host = 'localhost';
my $port = '3306';
my $database = 'chatapp';
my $username = 'duck';
my $db_password = 'Welcome@123';

my $dsn = "DBI:mysql:database=$database;host=$host;port=$port";
my $dbh = DBI->connect($dsn, $username, $db_password, { RaiseError => 1, AutoCommit => 1 }) or die "Couldn't connect to database: " . DBI->errstr;

# Check if user already exists
my $sth_check = $dbh->prepare("SELECT * FROM chatusers WHERE emailaddress = ? OR phonenum = ?");
$sth_check->execute($emailaddress, $phone);

if ($sth_check->fetchrow_array) {
    my $response = {
        success => 0,
        message => "User with given email address or phone number already exists. Please login to continue.",
    };
    print encode_json($response);
    exit;
}

$sth_check->finish;

# Insert new user
my $sth_insert = $dbh->prepare("INSERT INTO chatusers (name, emailaddress, password, phonenum) VALUES (?, ?, ?, ?)");
$sth_insert->execute($name, $emailaddress, $password, $phone);
$sth_insert->finish;

# Success response
my $response = {
    success => 1,
    message => "Registration successful. Please login to continue.",
};
print encode_json($response);

$dbh->disconnect;
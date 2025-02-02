#!/usr/bin/perl

use strict;
use warnings;
use CGI;
use JSON;
use DBI;
use Email::Valid;

my $host = 'localhost';
my $port = '3306';
my $database = 'chatapp';
my $username = 'duck';
my $db_password = 'Welcome@123';

my $dsn = "DBI:mysql:database=$database;host=$host;port=$port";
my $dbh = DBI->connect($dsn, $username, $db_password, { RaiseError => 1, AutoCommit => 1 }) or die "Couldn't connect to database: " . DBI->errstr;

# Get POST data
my $cgi = CGI->new;
my $json = $cgi->param('POSTDATA');
my $data = decode_json($json);

my $new_password = $data->{'newPassword'};
my $confirmPassword = $data->{'confirmPassword'};
my $otp_method = $data->{'otpMethod'};
my $otp_input = $data->{'otpInput'};

# Validate passwords
if (length($new_password) < 8 || $new_password !~ /.*\d.*\d.*/) {
    my $response = {
        status => 'error',
        message => 'Password must be at least 8 characters long and contain at least 2 numbers.'
    };
    print $cgi->header('application/json');
    print encode_json($response);
    exit;
}

if ($new_password ne $confirmPassword) {
    my $response = {
        status => 'error',
        message => 'Passwords do not match.'
    };
    print $cgi->header('application/json');
    print encode_json($response);
    exit;
}

# Validate OTP input
if ($otp_method eq 'sms') {
    unless ($otp_input =~ /^\d{10}$/) {
        my $response = {
            status => 'error',
            message => 'Please enter a valid 10-digit phone number.'
        };
        print $cgi->header('application/json');
        print encode_json($response);
        exit;
    }
} elsif ($otp_method eq 'email') {
    unless (Email::Valid->address($otp_input)) {
        my $response = {
            status => 'error',
            message => 'Please enter a valid email address.'
        };
        print $cgi->header('application/json');
        print encode_json($response);
        exit;
    }
}

# Prepare SQL statement
my $statement;
if ($otp_method eq 'sms') {
    $statement = $dbh->prepare("UPDATE chatusers SET password = ? WHERE phonenum = ?");
} elsif ($otp_method eq 'email') {
    $statement = $dbh->prepare("UPDATE chatusers SET password = ? WHERE emailaddress = ?");
}

# Execute SQL statement
$statement->execute($new_password, $otp_input) or die "Database Error: $DBI::errstr\n";

# Respond with success
my $response = {
    status => 'success',
    message => 'Password reset successfully'
};

print $cgi->header('application/json');
print encode_json($response);
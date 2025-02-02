#!/usr/bin/perl

use strict;
use warnings;
use CGI;
use DBI;
use JSON;
use Email::Valid;

# Print the content type, allowing CORS
print "Content-Type: application/json\n";
print "Access-Control-Allow-Origin: *\n\n";

# Read POST data
my $cgi = CGI->new;
my $json_text = $cgi->param('POSTDATA') || '{}';
my $data = decode_json($json_text);
my $otp = $data->{otp} || '';
my $otpMethod = $data->{otpMethod} || '';
my $otpInput = $data->{otpInput} || '';

# Database configuration
my $host = 'localhost';
my $port = '3306';
my $database = 'chatapp';
my $username = 'duck';
my $db_password = 'Welcome@123';

my $dsn = "DBI:mysql:database=$database;host=$host;port=$port";
my $dbh = DBI->connect($dsn, $username, $db_password, { RaiseError => 1, AutoCommit => 1 }) or die "Couldn't connect to database: " . DBI->errstr;

# Validate OTP input
my $validation_error;
if ($otpMethod eq 'sms') {
    unless ($otpInput =~ /^\d{10}$/) {
        $validation_error = 'Please enter a valid 10-digit phone number.';
    }
} elsif ($otpMethod eq 'email') {
    unless (Email::Valid->address($otpInput)) {
        $validation_error = 'Please enter a valid email address.';
    }
}

# Validate OTP
unless ($otp =~ /^\d+$/) {
    $validation_error = 'OTP must be numeric.';
}

if ($validation_error) {
    print encode_json({ status => 'error', message => $validation_error });
    exit;
}

# Validate OTP in the database
my $validation_result = validate_otp($otpMethod, $otpInput, $otp, $dbh);

if ($validation_result->{status} eq 'success') {
    print encode_json({ status => 'success', message => 'OTP verified successfully' });
} else {
    print encode_json({ status => 'error', message => $validation_result->{message} });
}

$dbh->disconnect;

sub validate_otp {
    my ($otpMethod, $otpInput, $otp, $dbh) = @_;

    my $where_clause;
    if ($otpMethod eq 'sms') {
        $where_clause = "phonenum = ?";
    } elsif ($otpMethod eq 'email') {
        $where_clause = "emailaddress = ?";
    }

    # Check OTP in chatusers table
    my $sth_check_otp = $dbh->prepare("SELECT * FROM chatusers WHERE $where_clause AND otp = ?");
    $sth_check_otp->execute($otpInput, $otp);

    if (my $row = $sth_check_otp->fetchrow_arrayref) {
        return { status => 'success' };  # OTP is valid
    } else {
        return { status => 'error', message => 'Incorrect OTP. Please try again.' };  # OTP is invalid
    }

    $sth_check_otp->finish;
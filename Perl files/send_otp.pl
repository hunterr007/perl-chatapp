#!/usr/bin/perl

BEGIN {
    unshift @INC, '/usr/lib/x86_64-linux-gnu/perl-base';
    unshift @INC, '/usr/share/perl/5.34.0';
    unshift @INC, '/usr/local/lib/x86_64-linux-gnu/perl/5.34.0';
    unshift @INC, '/home/nmishra/perl5/lib/perl5';
}

use strict;
use warnings;
use CGI qw(:standard);
use DBI;
use JSON;
use POSIX qw(strftime);
use SMS::Send;
use Data::Dumper;
use Email::Sender::Simple qw(sendmail);
use Email::Sender::Transport::SMTP::TLS;
use Email::Simple;

my $host = 'localhost';
my $port = '3306';
my $database = 'chatapp';
my $username = 'duck';
my $db_password = 'Welcome@123';

my $dsn = "DBI:mysql:database=$database;host=$host;port=$port";
my $dbh = DBI->connect($dsn, $username, $db_password, { RaiseError => 1, AutoCommit => 1 }) or die "Couldn't connect to database: " . DBI->errstr;

# Read POST data
my $cgi = CGI->new;
my $json_text = $cgi->param('POSTDATA') || '{}';
print STDERR "Received POSTDATA: $json_text\n";

my $data = decode_json($json_text);
my $otp_method = $data->{otpMethod} || '';  # Added default '' to handle undefined otpMethod
my $otp_input = lc($data->{otpInput} || '');  # Added default '' to handle undefined otpInput

print STDERR "Received otpMethod: $otp_method\n";
print STDERR "Received otpInput: $otp_input\n";

# Validation
if ($otp_method eq 'sms') {
    unless ($otp_input =~ /^\d{10}$/) {
        print "Content-Type: application/json\n\n";
        print encode_json({ status => 'error', message => 'Please enter a valid 10-digit phone number.' });
        exit;
    }
} elsif ($otp_method eq 'email') {
    unless ($otp_input =~ /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/) {
        print "Content-Type: application/json\n\n";
        print encode_json({ status => 'error', message => 'Please enter a valid email address.' });
        exit;
    }
}

my $sth_check_user;
if ($otp_method eq 'sms') {
    $sth_check_user = $dbh->prepare("SELECT phonenum FROM chatusers WHERE phonenum = ?");
} elsif ($otp_method eq 'email') {
    $sth_check_user = $dbh->prepare("SELECT emailaddress FROM chatusers WHERE LOWER(emailaddress) = ?");
}

$sth_check_user->execute($otp_input);

if (my $user_row = $sth_check_user->fetchrow_arrayref) {
    # Generate a random 6-digit OTP
    my $otp = int(100000 + rand(900000));
    my $time = strftime "%Y-%m-%d %H:%M:%S", localtime;

    my $sth_check_otp;
    if ($otp_method eq 'sms') {
        $sth_check_otp = $dbh->prepare("SELECT phonenum FROM chatusers WHERE phonenum = ?");
    } elsif ($otp_method eq 'email') {
        $sth_check_otp = $dbh->prepare("SELECT emailaddress FROM chatusers WHERE LOWER(emailaddress) = ?");
    }

    $sth_check_otp->execute($otp_input);

    # Update or insert the OTP and timestamp
    if (my $otp_row = $sth_check_otp->fetchrow_arrayref) {
        my $sth_update;
        if ($otp_method eq 'sms') {
            $sth_update = $dbh->prepare("UPDATE chatusers SET otp = ? WHERE phonenum = ?");
            $sth_update->execute($otp, $otp_input);
        } elsif ($otp_method eq 'email') {
            $sth_update = $dbh->prepare("UPDATE chatusers SET otp = ? WHERE LOWER(emailaddress) = ?");
            $sth_update->execute($otp, $otp_input);
        }
    }
        # else {
        # my $sth_insert;
        # if ($otp_method eq 'sms') {
            # $sth_insert = $dbh->prepare("INSERT INTO chatusers (phonenum, otp, time) VALUES (?, ?, ?)");
            # $sth_insert->execute($otp_input, $otp, $time);
        # } elsif ($otp_method eq 'email') {
            # $sth_insert = $dbh->prepare("INSERT INTO chatusers (emailaddress, otp, time) VALUES (?, ?, ?)");
            # $sth_insert->execute($otp_input, $otp, $time);
        # }
    # }

    $sth_check_otp->finish;

    if ($otp_method eq 'sms') {
        # Send the OTP via SMS
        my $sms_response = send_sms($otp_input, "Your OTP is $otp");
        if ($sms_response) {
            # Return success response
            print "Content-Type: application/json\n\n";
            print encode_json({ status => 'success', otp => $otp });
        } else {
            # Return error response
            print "Content-Type: application/json\n\n";
            print encode_json({ status => 'error', message => 'Failed to send OTP via SMS.' });
        }
    } elsif ($otp_method eq 'email') {
        # Send the OTP via email
        my $email_response = send_email($otp_input, "Your OTP is $otp");
        if ($email_response) {
            # Return success response
            print "Content-Type: application/json\n\n";
            print encode_json({ status => 'success', otp => $otp });
        } else {
            # Return error response
            print "Content-Type: application/json\n\n";
            print encode_json({ status => 'error', message => 'Failed to send OTP via email.' });
        }
    }
} else {
    # Return error response if the phone or email does not exist
    print "Content-Type: application/json\n\n";
    if ($otp_method eq 'sms') {
        print encode_json({ status => 'error', message => 'Phone number is not registered. Please enter a registered phone number.' });
    } elsif ($otp_method eq 'email') {
        print encode_json({ status => 'error', message => 'Email address is not registered. Please enter a registered email address.' });
    }
}

$sth_check_user->finish;
$dbh->disconnect;

# Function for sending SMS
sub send_sms {
    my ($phone, $message) = @_;

    $phone = "+91$phone"; # Assuming the country code for India

    my $sender = SMS::Send->new('Twilio',
        _accountsid => 'AC2faa70e57adc52323d13a8dad9461c48',
        _authtoken  => '6aba98a5daf92fa468ae10ee041b1960',
        _from       => '+17069792452',
    );

    my $sent = $sender->send_sms(
        text => "$message",
        to   => "$phone",
    );

    return $sent ? 1 : 0;
}

sub send_email {
    my ($email, $message) = @_;
    my $email_obj  = Email::Simple->create(
        header => [
            To      => $email,
            From    => 'nidhimishra28@gmail.com',
            Subject => 'Your OTP Code',
        ],
        body => $message,
    );

    my $transport = Email::Sender::Transport::SMTP::TLS->new(
        {
            host     => 'smtp.gmail.com',
            port     => 587,
            username => 'nidhimishra28@gmail.com',
            password => 'jmum cdnz xljd yqpx',
        }
    );

    eval {
        sendmail($email_obj, { transport => $transport });
    };

    if ($@) {
        print STDERR "Email sending failed: $@\n";
        return 0;
    } else {
        return 1;
    }
}
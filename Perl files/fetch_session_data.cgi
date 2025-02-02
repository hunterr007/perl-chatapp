#!/usr/bin/perl
use strict;
use warnings;
use CGI;
use CGI::Session;
use Data::Dumper;

# Initialize CGI object
my $cgi = CGI->new;

# Start or retrieve the session
my $session = CGI::Session->new($cgi);

warn"###### FETCH CGI    ########".Dumper($session);

# Fetch email (username) from session
my $email = $session->param('email') || 'Not logged in';

# Set content type
print $cgi->header('application/json');

# Print JSON response
print qq|{"email": "$email"}|;
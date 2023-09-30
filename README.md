# CSC361 A1 SmartClient

## Intro

SmartClient is an advanced Python utility designed to interact with web servers and provide insights about their behavior and features.

## Features

HTTP/2 Support: Determines if the server supports the HTTP/2 protocol.
Cookie Handling: Extracts information about cookies, their expiration times, and their domain names.
Password Protection Detection: Determines if the requested page is password-protected.
Redirection: Handles and follows HTTP 301 and 302 redirections.
Scheme Detection: Detects and considers the URL scheme (http:// or https://).

## Prerequisites

Python must be installed on your system. The utility uses the following Python standard library modules:

- socket
- ssl
- re
- sys
  
## Usage

To use the SmartClient, provide the URL you wish to query as a command-line argument:

```bash
python3 SmartClient.py <URL>
```

For example:

```bash
python SmartClient.py https://example.com
```

## Output

SmartClient will produce clear and structured output, summarizing:

Whether the target supports HTTP/2.
All cookies set by the server, along with their attributes.
If the page is password-protected.
Redirections, if any.

## Implementation Details
The SmartClient class contains methods to establish both default and SSL socket connections.
Redirects are handled with a limit to prevent infinite loops.
The script contains tons of error handling to address various possible exceptions.

 -------------------------------------------------------------------------------
     _____                _                           _
    | ____| _ __    __ _ (_) _ __    ___   ___  _ __ (_) _ __    __ _
    |  _|  | '_ \  / _` || || '_ \  / _ \ / _ \| '__|| || '_ \  / _` |
    | |___ | | | || (_| || || | | ||  __/|  __/| |   | || | | || (_| |
    |_____||_| |_| \__, ||_||_| |_| \___| \___||_|   |_||_| |_| \__, |
                    |___/                                        |___/

-------------------------------------------------------------------------------

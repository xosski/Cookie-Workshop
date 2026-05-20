Cookie Workshop — Beginner Learning Guide
What Is Cookie Workshop?

Cookie Workshop is a browser testing tool designed to help developers, QA engineers, students, and authorized security testers understand how browser cookies work.

Cookies are small pieces of data stored by websites inside your browser. They are commonly used for:

login sessions
remembering preferences
shopping carts
authentication
analytics
security settings

This project provides a safe environment for learning how cookies behave during normal web application use.

Important Legal & Ethical Notice

Use Cookie Workshop only on:

websites you own
local development environments
training labs
systems you are explicitly authorized to test

Never use this tool to:

access unauthorized accounts
steal session tokens
impersonate users
bypass authentication
interfere with third-party systems

Responsible security work protects systems.
It does not abuse them.

What You’ll Learn

Using Cookie Workshop can help you understand:

How websites store session data
What Secure cookies do
What SameSite settings mean
How cookie expiration works
Why paths and domains matter
How login sessions persist
Why modern browsers protect HttpOnly cookies

Think of it like a microscope for browser state.

Cookie Basics

A cookie usually contains:

Property	Purpose
Name	Identifier
Value	Stored data
Domain	Which site can use it
Path	Which URL paths can access it
Expires	When it is removed
Secure	HTTPS-only access
HttpOnly	Hidden from JavaScript
SameSite	Cross-site behavior rules

Example:

session_id=abc123

This tells the browser:

“Remember this value for later requests.”

Understanding SameSite

Modern browsers use SameSite to reduce certain web attacks.

Lax

Most common default.

Allows:

normal navigation
safer cross-site handling

Blocks many background cross-site requests.

Strict

Most restrictive.

Cookies only work when directly visiting the site.

Useful for:

highly sensitive sessions
admin portals
None

Allows full cross-site usage.

Requires:

HTTPS
Secure=true

Common for:

APIs
embedded services
federated login systems
What Secure Does

A Secure cookie:

Secure=true

means:

“Only send this cookie over HTTPS.”

This prevents accidental transmission over insecure HTTP connections.

What HttpOnly Does

An HttpOnly cookie:

HttpOnly=true

cannot be read by JavaScript running in the page.

This helps reduce:

XSS token theft
browser-side session leakage

Important:
Cookie Workshop should be used to understand these protections — not bypass them.

Installing the Extension
Step 1 — Open Extensions Page

In Chrome or Edge:

chrome://extensions
Step 2 — Enable Developer Mode

Toggle:

Developer Mode → ON
Step 3 — Load the Extension

Click:

Load unpacked

Select the folder:

cookie-workshop-extension

The extension should now appear in your toolbar.

Basic Usage
Viewing Cookies
Open a local or authorized test website.
Click the Cookie Workshop icon.
Press:
Load Current Site Cookies

You will see:

cookie names
values
paths
security settings
Creating a Cookie

Example test cookie:

Field	Value
Name	theme
Value	darkmode
Path	/
SameSite	Lax

Click:

Set Cookie

Refresh the site and observe behavior.

Deleting a Cookie

Press:

Delete

next to the cookie entry.

You can observe:

logout behavior
preference resets
session invalidation

This helps explain how many web applications maintain state.

Learning Exercises
Exercise 1 — Session Persistence
Create a cookie.
Refresh the page.
Restart the browser.
Observe whether it remains.

Question:

What determines persistence?

Exercise 2 — Path Restrictions

Create:

Path=/admin

Observe:

where the cookie appears
which pages receive it
Exercise 3 — Secure Cookies

Test:

Secure=true

Compare:

HTTP behavior
HTTPS behavior
Exercise 4 — SameSite

Create multiple cookies using:

Lax
Strict
None

Study:

browser behavior
navigation differences
request handling
Why Browsers Protect Cookies

Modern browsers intentionally restrict:

cross-site access
JavaScript visibility
insecure transport
unauthorized modification

These protections exist because cookies often contain:

login sessions
authentication state
user preferences
security tokens

Understanding the protections is part of becoming a better developer and defender.

Recommended Learning Topics

After learning cookies, explore:

HTTP requests
sessions
CSRF protection
XSS prevention
OAuth
JWT tokens
browser storage APIs
secure authentication design
Final Reminder

Security knowledge is a tool.

In responsible hands:

it improves systems
protects users
strengthens infrastructure

The goal of Cookie Workshop is education, testing, and understanding — not abuse.

Or in GhostCore terms:

The cookie remembers.
The browser decides.
The engineer learns where trust begins and ends.

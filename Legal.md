# Cookie Workshop Extension

Cookie Workshop is a browser extension for **authorized cookie testing** during web development, QA, and approved security assessments.

## Authorized Use Only

Use this tool only on systems you own, control, or have explicit written permission to test.

Do **not** use this tool to:
- Access accounts without permission
- Bypass authentication
- Steal, export, or reuse session cookies
- Modify cookies on third-party systems without authorization
- Evade security controls
- Perform unauthorized red-team activity

You are responsible for complying with all applicable laws, contracts, rules of engagement, and platform policies.

## Purpose

Cookie Workshop is intended for:
- Local development testing
- QA cookie validation
- SameSite / Secure / Path testing
- Authorized pentesting
- Debugging login/session behavior
- Testing cookie deletion and expiration handling

## Features

- View cookies for the current active tab
- Add or update cookies for the current site
- Delete selected cookies
- Test `Secure` and `SameSite` behavior
- Current-tab focused workflow
- No remote upload
- No automatic harvesting
- No background cookie collection

## Safety Notes

This extension should not be used to collect or exfiltrate cookies.

HttpOnly cookies may be visible through browser APIs depending on browser behavior and permissions, but they should not be copied, exported, reused, or transferred outside the authorized test environment.

## Installation

1. Open Chrome or Edge.
2. Go to `chrome://extensions`.
3. Enable **Developer Mode**.
4. Click **Load unpacked**.
5. Select the `cookie-workshop-extension` folder.

## Usage

1. Open the authorized target site.
2. Click the Cookie Workshop extension icon.
3. Click **Load Current Site Cookies**.
4. Review, edit, or delete cookies only as allowed by your test scope.

## Recommended Rules of Engagement

Before using this tool, confirm:

- The target domain is in scope.
- You have written authorization.
- Cookie/session testing is allowed.
- Account takeover testing is explicitly permitted if relevant.
- You will not retain sensitive session data after testing.
- Findings will be reported responsibly.

## Disclaimer

This project is provided for lawful, ethical, and authorized testing only.  
Misuse may violate laws, contracts, or platform policies.

The author assumes no responsibility for unauthorized use.
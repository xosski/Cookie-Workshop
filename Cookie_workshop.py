# cookie_workshop.py
from datetime import datetime, timedelta, timezone

from flask import Flask, make_response, redirect, render_template_string, request, url_for

app = Flask(__name__)

SAMESITE_VALUES = {"Lax", "Strict", "None"}

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cookie Workshop</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem; max-width: 1100px; }
    label { display: block; margin: .6rem 0 .2rem; font-weight: 600; }
    input, select, textarea, button { font: inherit; padding: .45rem; }
    input[type="checkbox"] { padding: 0; }
    textarea { width: 100%; min-height: 5rem; }
    table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
    th, td { border: 1px solid #ccc; padding: .5rem; text-align: left; vertical-align: top; }
    th { background: #f5f5f5; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: .75rem; }
    .inline { display: inline-flex; gap: .5rem; align-items: center; margin-right: 1rem; }
    .panel { border: 1px solid #ddd; border-radius: .5rem; padding: 1rem; margin: 1rem 0; }
    .message { padding: .75rem; border-radius: .4rem; margin: 1rem 0; }
    .error { background: #ffecec; border: 1px solid #ffb3b3; }
    .success { background: #eaf7ea; border: 1px solid #a8d8a8; }
    .muted { color: #555; }
    code { background: #f3f3f3; padding: .1rem .25rem; }
  </style>
</head>
<body>
<h1>Cookie Workshop</h1>
<p class="muted">
  Local testing tool for cookies on this app/domain only. Browsers only accept cookies for the
  host/path rules you choose here; this tool does not read browser cookie stores or modify third-party domains.
</p>

{% if message %}
  <div class="message {{ status }}">{{ message }}</div>
{% endif %}

<h2>Current Cookies</h2>
<p><b>Request host:</b> <code>{{ host }}</code></p>
<p><b>Raw Cookie header:</b> <code>{{ raw_cookie or "(none)" }}</code></p>
<table>
  <thead><tr><th>Name</th><th>Value</th><th>Quick actions</th></tr></thead>
  <tbody>
{% for k, v in cookies.items() %}
    <tr>
      <td><code>{{ k }}</code></td>
      <td><code>{{ v }}</code></td>
      <td>
        <form method="POST" action="{{ url_for('delete_cookie') }}">
          <input type="hidden" name="name" value="{{ k }}">
          <input type="hidden" name="path" value="/">
          <button type="submit">Delete at /</button>
        </form>
      </td>
    </tr>
{% else %}
    <tr><td colspan="3">No cookies set.</td></tr>
{% endfor %}
  </tbody>
</table>

<section class="panel">
  <h2>Set / Update Cookie</h2>
  <form method="POST" action="{{ url_for('set_cookie') }}">
    <div class="grid">
      <div>
        <label for="name">Name</label>
        <input id="name" name="name" placeholder="session_id" required>
      </div>
      <div>
        <label for="value">Value</label>
        <input id="value" name="value" placeholder="cookie value" required>
      </div>
      <div>
        <label for="path">Path</label>
        <input id="path" name="path" value="/" placeholder="/">
      </div>
      <div>
        <label for="domain">Domain (optional)</label>
        <input id="domain" name="domain" placeholder="leave blank for host-only">
      </div>
      <div>
        <label for="samesite">SameSite</label>
        <select id="samesite" name="samesite">
          <option value="Lax">Lax</option>
          <option value="Strict">Strict</option>
          <option value="None">None</option>
        </select>
      </div>
      <div>
        <label for="expires_mode">Expiration</label>
        <select id="expires_mode" name="expires_mode">
          <option value="days">Expires in days</option>
          <option value="session">Session cookie</option>
          <option value="max_age">Max-Age seconds</option>
          <option value="expires_at">Absolute UTC datetime</option>
        </select>
      </div>
      <div>
        <label for="days">Days</label>
        <input id="days" name="days" type="number" value="7" min="1">
      </div>
      <div>
        <label for="max_age">Max-Age seconds</label>
        <input id="max_age" name="max_age" type="number" min="0" placeholder="3600">
      </div>
      <div>
        <label for="expires_at">Expires at UTC</label>
        <input id="expires_at" name="expires_at" type="datetime-local">
      </div>
    </div>

    <p>
      <label class="inline"><input type="checkbox" name="secure"> Secure</label>
      <label class="inline"><input type="checkbox" name="httponly"> HttpOnly</label>
    </p>

    <button type="submit">Save Cookie</button>
  </form>
</section>

<section class="panel">
  <h2>Set Multiple Cookies from a Cookie Header</h2>
  <p class="muted">Paste a simple <code>Cookie</code> request header such as <code>a=1; b=2</code>. Attributes below are applied to every cookie.</p>
  <form method="POST" action="{{ url_for('bulk_set_cookies') }}">
    <label for="cookie_header">Cookie header</label>
    <textarea id="cookie_header" name="cookie_header" placeholder="name=value; theme=dark" required></textarea>
    <div class="grid">
      <div>
        <label for="bulk_path">Path</label>
        <input id="bulk_path" name="path" value="/" placeholder="/">
      </div>
      <div>
        <label for="bulk_domain">Domain (optional)</label>
        <input id="bulk_domain" name="domain" placeholder="leave blank for host-only">
      </div>
      <div>
        <label for="bulk_days">Days</label>
        <input id="bulk_days" name="days" type="number" value="7" min="1">
      </div>
      <div>
        <label for="bulk_samesite">SameSite</label>
        <select id="bulk_samesite" name="samesite">
          <option value="Lax">Lax</option>
          <option value="Strict">Strict</option>
          <option value="None">None</option>
        </select>
      </div>
    </div>
    <p>
      <label class="inline"><input type="checkbox" name="secure"> Secure</label>
      <label class="inline"><input type="checkbox" name="httponly"> HttpOnly</label>
    </p>
    <button type="submit">Set Header Cookies</button>
  </form>
</section>

<section class="panel">
  <h2>Delete Cookie</h2>
  <form method="POST" action="{{ url_for('delete_cookie') }}">
    <div class="grid">
      <div>
        <label for="delete_name">Name</label>
        <input id="delete_name" name="name" placeholder="cookie name" required>
      </div>
      <div>
        <label for="delete_path">Path</label>
        <input id="delete_path" name="path" value="/" placeholder="/">
      </div>
      <div>
        <label for="delete_domain">Domain (optional)</label>
        <input id="delete_domain" name="domain" placeholder="must match cookie domain">
      </div>
    </div>
    <button type="submit">Delete</button>
  </form>
</section>

<section class="panel">
  <h2>Clear Visible Cookies</h2>
  <p class="muted">Deletion must match the cookie's path/domain. Use the same values you used when creating them.</p>
  <form method="POST" action="{{ url_for('clear_cookies') }}">
    <div class="grid">
      <div>
        <label for="clear_path">Path</label>
        <input id="clear_path" name="path" value="/" placeholder="/">
      </div>
      <div>
        <label for="clear_domain">Domain (optional)</label>
        <input id="clear_domain" name="domain" placeholder="leave blank for host-only">
      </div>
    </div>
    <button type="submit">Clear All Visible</button>
  </form>
</section>
</body>
</html>
"""


def redirect_home(message, status="success"):
    return redirect(url_for("index", message=message, status=status))


def normalized_path():
    path = request.form.get("path", "/").strip() or "/"
    return path if path.startswith("/") else f"/{path}"


def optional_domain():
    return request.form.get("domain", "").strip() or None


def cookie_options():
    samesite = request.form.get("samesite", "Lax")
    secure = "secure" in request.form

    if samesite not in SAMESITE_VALUES:
        raise ValueError("SameSite must be Lax, Strict, or None.")
    if samesite == "None" and not secure:
        raise ValueError("Modern browsers require Secure when SameSite=None.")

    return {
        "path": normalized_path(),
        "domain": optional_domain(),
        "secure": secure,
        "httponly": "httponly" in request.form,
        "samesite": samesite,
    }


def expiration_options():
    mode = request.form.get("expires_mode", "days")
    if mode == "session":
        return {}
    if mode == "max_age":
        max_age = int(request.form.get("max_age") or 0)
        if max_age < 0:
            raise ValueError("Max-Age cannot be negative.")
        return {"max_age": max_age}
    if mode == "expires_at":
        raw_expires_at = request.form.get("expires_at", "").strip()
        if not raw_expires_at:
            raise ValueError("Absolute expiration requires a UTC datetime.")
        expires = datetime.fromisoformat(raw_expires_at).replace(tzinfo=timezone.utc)
        return {"expires": expires}

    days = int(request.form.get("days") or 7)
    if days < 1:
        raise ValueError("Days must be at least 1.")
    return {"expires": datetime.now(timezone.utc) + timedelta(days=days)}


def parse_cookie_header(header):
    pairs = []
    for part in header.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise ValueError(f"Invalid cookie pair: {part!r}")
        name, value = part.split("=", 1)
        name = name.strip()
        if not name:
            raise ValueError("Cookie names cannot be blank.")
        pairs.append((name, value.strip()))
    if not pairs:
        raise ValueError("Cookie header did not contain any name=value pairs.")
    return pairs


@app.route("/")
def index():
    return render_template_string(
        HTML,
        cookies=request.cookies,
        host=request.host,
        raw_cookie=request.headers.get("Cookie", ""),
        message=request.args.get("message"),
        status=request.args.get("status", "success"),
    )


@app.route("/set", methods=["POST"])
def set_cookie():
    try:
        name = request.form["name"].strip()
        if not name:
            raise ValueError("Cookie name cannot be blank.")

        response = make_response(redirect_home(f"Saved cookie {name!r}."))
        response.set_cookie(
            key=name,
            value=request.form["value"],
            **cookie_options(),
            **expiration_options(),
        )
        return response
    except (KeyError, TypeError, ValueError) as error:
        return redirect_home(str(error), "error")


@app.route("/bulk-set", methods=["POST"])
def bulk_set_cookies():
    try:
        pairs = parse_cookie_header(request.form["cookie_header"])
        options = cookie_options()
        days = int(request.form.get("days") or 7)
        if days < 1:
            raise ValueError("Days must be at least 1.")
        expires = datetime.now(timezone.utc) + timedelta(days=days)

        response = make_response(redirect_home(f"Saved {len(pairs)} cookies from header."))
        for name, value in pairs:
            response.set_cookie(key=name, value=value, **options, expires=expires)
        return response
    except (KeyError, TypeError, ValueError) as error:
        return redirect_home(str(error), "error")


@app.route("/delete", methods=["POST"])
def delete_cookie():
    try:
        name = request.form["name"].strip()
        if not name:
            raise ValueError("Cookie name cannot be blank.")

        response = make_response(redirect_home(f"Deleted cookie {name!r}."))
        response.delete_cookie(name, path=normalized_path(), domain=optional_domain())
        return response
    except (KeyError, ValueError) as error:
        return redirect_home(str(error), "error")


@app.route("/clear", methods=["POST"])
def clear_cookies():
    path = normalized_path()
    domain = optional_domain()
    response = make_response(redirect_home(f"Cleared {len(request.cookies)} visible cookies."))
    for name in request.cookies.keys():
        response.delete_cookie(name, path=path, domain=domain)
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True, port=5000)

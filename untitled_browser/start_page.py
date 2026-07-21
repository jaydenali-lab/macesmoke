"""The built-in new-tab start page."""

START_PAGE_TITLE = "New Tab"

START_PAGE_HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>New Tab</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; margin: 0; }
  body {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 28px;
    background: radial-gradient(1200px 600px at 50% -10%, #2a2a35 0%, #17171d 60%);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    color: #e8e8ee;
  }
  h1 { font-size: 42px; font-weight: 300; letter-spacing: 0.04em; }
  h1 b { font-weight: 700; }
  form { width: min(620px, 84vw); }
  input {
    width: 100%;
    padding: 15px 24px;
    font-size: 17px;
    color: inherit;
    background: #232330;
    border: 1px solid #35354a;
    border-radius: 999px;
    outline: none;
  }
  input:focus { border-color: #6c6cf0; box-shadow: 0 0 0 3px rgba(108, 108, 240, 0.25); }
  p { color: #77778c; font-size: 13px; }
</style>
</head>
<body>
  <h1><b>Untitled</b> Browser</h1>
  <form id="f" autocomplete="off">
    <input id="q" placeholder="Search the web or enter an address" autofocus>
  </form>
  <p>Ctrl+T new tab &nbsp;&middot;&nbsp; Ctrl+L address bar &nbsp;&middot;&nbsp; Ctrl+W close tab</p>
  <script>
    var form = document.getElementById('f');
    var box = document.getElementById('q');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var t = box.value.trim();
      if (!t) return;
      var u;
      if (/^[a-zA-Z][a-zA-Z0-9+.\\-]*:\\/\\//.test(t) || t.indexOf('about:') === 0) {
        u = t;
      } else if (!/\\s/.test(t) && (t.indexOf('.') !== -1 || t.indexOf('localhost') === 0)) {
        u = 'https://' + t;
      } else {
        u = 'https://duckduckgo.com/?q=' + encodeURIComponent(t);
      }
      window.location.href = u;
    });
  </script>
</body>
</html>
"""

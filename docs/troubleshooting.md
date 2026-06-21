# GHPR Dashboard Troubleshooting

## Chrome / Google Translate causes `removeChild` NotFoundError

Symptom:

```text
NotFoundError: Failed to execute 'removeChild' on 'Node'
```

Observed context:

- The error can appear while viewing the local Streamlit app, for example `localhost:8501` or `localhost:8502`.
- Screenshots showed Chrome / Google Translate translating the Streamlit page.
- The Dashboard data files and Plotly figures may still be valid while the browser frontend shows this error.

Likely cause:

Chrome / Google Translate can mutate the Streamlit / React DOM after Streamlit renders it. Streamlit then tries to update or remove a node that the translator has already changed, producing the `removeChild` frontend error.

Current mitigation in GHPR:

- The Dashboard injects `<meta name="google" content="notranslate">`.
- The main Streamlit containers are marked with `class="notranslate"` and `translate="no"` where browser access allows it.
- The Dashboard displays a warning asking users not to auto-translate localhost.
- The Dashboard itself includes Chinese text so users should not need browser translation for normal use.

What to do:

1. Turn off Chrome / Google Translate for the GHPR localhost page.
2. Refresh the page.
3. If the error disappears after translation is disabled, treat it as a browser translation DOM mutation issue rather than a GHPR data issue.
4. If the error still appears with translation disabled, capture the page name, browser console text, and the latest `outputs/reports/update_log.md`.

Research scope note:

GHPR is a historical statistics and research reference dashboard. It does not connect to TradeDock, broker APIs, or account data.

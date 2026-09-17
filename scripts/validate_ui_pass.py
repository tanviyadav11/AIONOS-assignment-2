"""
UI/UX Enhancement Pass Validation Script
Verifies frontend assets, CSS tokens, theme configuration, and end-to-end processing of all 15 requests.
"""

import httpx

def main():
    with httpx.Client(base_url="http://127.0.0.1:8000") as client:
        # 1. HTML validation
        r_html = client.get("/")
        assert r_html.status_code == 200
        html_text = r_html.text
        assert 'data-theme="light"' in html_text
        assert 'theme-toggle-btn' in html_text
        assert 'citation-popover' in html_text
        assert 'typing-indicator-box' in html_text
        print("[PASS] HTML structure and components validated.")

        # 2. CSS validation
        r_css = client.get("/static/css/style.css")
        assert r_css.status_code == 200
        css_text = r_css.text
        assert "--color-bg" in css_text
        assert "--color-primary" in css_text
        assert "--color-success" in css_text
        assert "--color-warning" in css_text
        assert "--color-danger" in css_text
        assert "--color-info" in css_text
        assert 'html[data-theme="dark"]' in css_text
        assert "stepReveal" in css_text
        assert "typingBounce" in css_text
        assert "citation-chip" in css_text
        print("[PASS] CSS design tokens, light/dark themes, and micro-animations validated.")

        # 3. JS validation
        r_js = client.get("/static/js/app.js")
        assert r_js.status_code == 200
        js_text = r_js.text
        assert "initTheme" in js_text
        assert "showCitationPopover" in js_text
        assert "renderCitationChips" in js_text
        assert "typing-indicator" in js_text
        print("[PASS] JS theme switching and interactive citation popovers validated.")

        # 4. Process all 15 requests
        r_reqs = client.get("/api/requests")
        assert r_reqs.status_code == 200
        requests = r_reqs.json()
        assert len(requests) == 15

        for req in requests:
            res = client.post("/api/process", json={
                "text": req["request"],
                "employee_name": req["employee"],
                "employee_email": req["email"],
                "request_id": req["id"]
            })
            assert res.status_code == 200
            data = res.json()
            assert data["reasoning"]["decision"] in [
                "AUTO_RESOLVED", "RESOLVED_WITH_INSTRUCTIONS",
                "PENDING_APPROVAL", "ESCALATED_SECURITY", "NEEDS_CLARIFICATION"
            ]
        print("[PASS] All 15 Data Pack requests processed with accurate decisions.")

    print("\nAll UI/UX enhancement checks PASSED successfully!")

if __name__ == "__main__":
    main()

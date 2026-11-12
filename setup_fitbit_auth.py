#!/usr/bin/env python3
"""
Fitbit OAuth Setup Script

Usage:
  uv run python setup_fitbit_auth.py --client-id YOUR_ID --client-secret YOUR_SECRET

This will:
1. Open browser to Fitbit authorization
2. Ask you to paste the redirect URL
3. Output your refresh token
"""

import argparse
import base64
import hashlib
import secrets
import urllib.parse
import webbrowser
import httpx


def main():
    parser = argparse.ArgumentParser(description="Fitbit OAuth Setup")
    parser.add_argument("--client-id", required=True, help="Fitbit Client ID")
    parser.add_argument("--client-secret", required=True, help="Fitbit Client Secret")
    args = parser.parse_args()

    print("=" * 50)
    print("Fitbit OAuth Setup")
    print("=" * 50)

    print("\nGenerating PKCE code verifier...")
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )

    redirect_uri = "http://127.0.0.1:8080/callback"
    scope = "activity heartrate sleep location nutrition profile settings weight"

    auth_url = (
        f"https://www.fitbit.com/oauth2/authorize?"
        f"client_id={args.client_id}&"
        f"response_type=code&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"scope={urllib.parse.quote(scope)}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256"
    )

    print("\n" + "=" * 50)
    print("OPEN THIS URL IN YOUR BROWSER:")
    print("=" * 50)
    print(auth_url)
    print("=" * 50)

    webbrowser.open(auth_url)

    print("\n1. Sign in to Fitbit if prompted")
    print("2. Click 'Allow' to authorize")
    print("3. You'll be redirected to a page that says 'Page not found' - that's OK")
    print("4. Look at the URL in your browser address bar")
    print("   It should look like: http://127.0.0.1:8080/callback?code=XYZ...")
    print("5. Copy that FULL URL and paste it below")

    redirect_url = input("\nPaste the redirect URL here: ").strip()

    parsed = urllib.parse.urlparse(redirect_url)
    query_params = urllib.parse.parse_qs(parsed.query)
    auth_code = query_params.get("code", [None])[0]

    if not auth_code:
        print("\nERROR: No authorization code found.")
        print("Make sure you paste the FULL URL.")
        return

    print("\nExchanging code for tokens...")

    credentials = base64.b64encode(f"{args.client_id}:{args.client_secret}".encode()).decode()

    try:
        response = httpx.post(
            "https://api.fitbit.com/oauth2/token",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "client_id": args.client_id,
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
            },
        )

        if response.status_code != 200:
            print(f"ERROR: {response.text}")
            return

        tokens = response.json()

        print("\n" + "=" * 50)
        print("SUCCESS! Add these to your .env file:")
        print("=" * 50)
        print(f"\nFITBIT_CLIENT_ID={args.client_id}")
        print(f"FITBIT_CLIENT_SECRET={args.client_secret}")
        print(f"FITBIT_REFRESH_TOKEN={tokens['refresh_token']}")
        print(f"\nFitbit User ID: {tokens['user_id']}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

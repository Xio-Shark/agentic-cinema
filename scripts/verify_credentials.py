#!/usr/bin/env python3
"""
Agentic Cinema: Credentials & Quota Verification Script
Checks and verifies Google Gemini API connectivity & quotas and Grafana Cloud instance readiness.
"""

import os
import sys
import time
import requests
from typing import Dict, Any

# Ensure stdout flushes immediately
sys.stdout.reconfigure(line_buffering=True)

# Try loading from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def print_header(title: str):
    print("\n" + "=" * 65)
    print(f"  🎬 {title}")
    print("=" * 65)

def verify_gemini_api(api_key: str) -> Dict[str, Any]:
    print_header("Google Gemini API & Quota Verification")
    
    if not api_key:
        print("❌ [Gemini] GEMINI_API_KEY / GOOGLE_API_KEY not found in environment or .env file.")
        return {"status": "MISSING_KEY"}

    print(f"🔑 Detected Gemini API Key: {api_key[:6]}...{api_key[-4:] if len(api_key) > 10 else '***'}")
    
    # Target production models available in 2026
    test_models = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-flash-latest",
        "gemini-3.7-flash"
    ]

    results = {}
    session = requests.Session()
    
    for model_name in test_models:
        print(f"\n🔍 Testing Model: [{model_name}]...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {"parts": [{"text": "Confirm API & Quota readiness for Agentic Cinema in 1 concise sentence."}]}
            ],
            "generationConfig": {
                "maxOutputTokens": 60,
                "temperature": 0.2
            }
        }
        start_time = time.time()
        try:
            r = session.post(url, json=payload, timeout=30)
            elapsed_ms = int((time.time() - start_time) * 1000)
            if r.status_code == 200:
                data = r.json()
                reply_text = data['candidates'][0]['content']['parts'][0]['text'].strip()
                usage = data.get('usageMetadata', {})
                print(f"   ✅ [PASS] Latency: {elapsed_ms}ms")
                print(f"   📊 Token Usage: prompt={usage.get('promptTokenCount')}, candidate={usage.get('candidatesTokenCount')}, total={usage.get('totalTokenCount')}")
                print(f"   💬 Response: \"{reply_text}\"")
                results[model_name] = {
                    "status": "PASS",
                    "latency_ms": elapsed_ms,
                    "response": reply_text
                }
            else:
                err_msg = r.text[:120]
                print(f"   ⚠️ [FAIL / STATUS {r.status_code}]: {err_msg}... ({elapsed_ms}ms)")
                results[model_name] = {
                    "status": "FAIL",
                    "latency_ms": elapsed_ms,
                    "error": err_msg
                }
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            print(f"   ❌ [EXCEPTION]: {e} ({elapsed_ms}ms)")
            results[model_name] = {
                "status": "ERROR",
                "latency_ms": elapsed_ms,
                "error": str(e)
            }
            
    return {"status": "SUCCESS", "results": results}

def verify_grafana_cloud(grafana_url: str, token: str) -> Dict[str, Any]:
    print_header("Grafana Cloud Connectivity Verification")
    
    if not grafana_url or not token:
        print("ℹ️ [Grafana] GRAFANA_URL or GRAFANA_SERVICE_ACCOUNT_TOKEN not fully set.")
        return {"status": "CONFIG_INCOMPLETE"}

    clean_url = grafana_url.rstrip("/")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"🌐 Target Grafana URL: {clean_url}")
    session = requests.Session()
    
    # 1. Test /api/org
    print("\n🔍 Step 1: Checking Organization Details (/api/org)...")
    try:
        r = session.get(f"{clean_url}/api/org", headers=headers, timeout=15)
        if r.status_code == 200:
            org_data = r.json()
            print(f"   ✅ Org ID: {org_data.get('id')}, Org Name: \"{org_data.get('name')}\"")
        else:
            print(f"   ⚠️ Status {r.status_code}: {r.text[:120]}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")

    # 2. Test /api/datasources
    print("\n🔍 Step 2: Listing Active Datasources (/api/datasources)...")
    datasources = []
    try:
        r = session.get(f"{clean_url}/api/datasources", headers=headers, timeout=15)
        if r.status_code == 200:
            ds_list = r.json()
            print(f"   ✅ Found {len(ds_list)} active datasource(s):")
            for ds in ds_list:
                ds_type = ds.get('type')
                ds_name = ds.get('name')
                print(f"      • [{ds_type}] {ds_name}")
                datasources.append(f"{ds_type}:{ds_name}")
        else:
            print(f"   ⚠️ Status {r.status_code}: {r.text[:120]}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")

    return {"status": "SUCCESS", "datasources_count": len(datasources)}

def main():
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    grafana_url = os.environ.get("GRAFANA_URL", "")
    grafana_token = os.environ.get("GRAFANA_SERVICE_ACCOUNT_TOKEN") or os.environ.get("GRAFANA_API_KEY") or ""

    print("🚀 Starting Agentic Cinema Live Pre-flight Checks...\n")
    
    gemini_res = verify_gemini_api(gemini_key)
    grafana_res = verify_grafana_cloud(grafana_url, grafana_token)

    print("\n" + "=" * 65)
    print("  📋 SUMMARY OF PRE-FLIGHT VERIFICATION")
    print("=" * 65)
    print(f"1. Gemini API Status : {gemini_res.get('status')}")
    print(f"2. Grafana Status    : {grafana_res.get('status')}")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""End-to-end integration test for Better Auth JWT flow.

This script:
1. Starts the frontend (Better Auth server) on port 3000
2. Starts the backend (FastAPI) on port 8000
3. Tests the complete JWT authentication flow
4. Cleans up processes when done

Usage:
    python scripts/e2e-integration-test.py
"""

import asyncio
import subprocess
import sys
import time
import os
from pathlib import Path

import httpx

# Configuration
FRONTEND_PORT = 3000
BACKEND_PORT = 8000
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"
TIMEOUT_SECONDS = 60

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_DIR = PROJECT_ROOT / "backend"


class ServiceManager:
    """Manages frontend and backend processes."""

    def __init__(self):
        self.frontend_process = None
        self.backend_process = None

    def start_frontend(self):
        """Start the Next.js frontend server."""
        print(f"Starting frontend on port {FRONTEND_PORT}...")
        env = os.environ.copy()
        env["PORT"] = str(FRONTEND_PORT)
        self.frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=FRONTEND_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return self.frontend_process

    def start_backend(self):
        """Start the FastAPI backend server."""
        print(f"Starting backend on port {BACKEND_PORT}...")
        env = os.environ.copy()
        env["API_PORT"] = str(BACKEND_PORT)
        self.backend_process = subprocess.Popen(
            ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", str(BACKEND_PORT)],
            cwd=BACKEND_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return self.backend_process

    def stop_all(self):
        """Stop all running processes."""
        if self.frontend_process:
            print("Stopping frontend...")
            self.frontend_process.terminate()
            self.frontend_process.wait(timeout=10)
        if self.backend_process:
            print("Stopping backend...")
            self.backend_process.terminate()
            self.backend_process.wait(timeout=10)


async def wait_for_service(url: str, name: str, timeout: int = TIMEOUT_SECONDS) -> bool:
    """Wait for a service to become available."""
    print(f"Waiting for {name} at {url}...")
    start = time.time()
    async with httpx.AsyncClient() as client:
        while time.time() - start < timeout:
            try:
                response = await client.get(url, timeout=2.0)
                if response.status_code < 500:
                    print(f"  {name} is ready!")
                    return True
            except Exception:
                pass
            await asyncio.sleep(1)
    print(f"  {name} did not start within {timeout}s")
    return False


async def test_better_auth_jwks():
    """Test that Better Auth JWKS endpoint is available."""
    print("\n=== Testing Better Auth JWKS Endpoint ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FRONTEND_URL}/api/auth/jwks")
        assert response.status_code == 200, f"JWKS endpoint returned {response.status_code}"
        data = response.json()
        assert "keys" in data, "JWKS response missing 'keys'"
        assert len(data["keys"]) > 0, "JWKS has no keys"
        print(f"  JWKS endpoint returned {len(data['keys'])} key(s)")
        return data


async def test_signup_flow():
    """Test user signup through Better Auth."""
    print("\n=== Testing Better Auth Signup Flow ===")
    async with httpx.AsyncClient() as client:
        email = f"test_{int(time.time())}@example.com"
        password = "SecureTestPass123!"

        response = await client.post(
            f"{FRONTEND_URL}/api/auth/sign-up/email",
            json={
                "email": email,
                "password": password,
                "name": "Test User",
            }
        )
        print(f"  Signup response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  User created: {email}")
            return {"email": email, "password": password, "data": data}
        else:
            print(f"  Signup failed: {response.text}")
            return None


async def test_signin_and_get_token():
    """Test user signin and JWT token retrieval."""
    print("\n=== Testing Better Auth Signin and Token Flow ===")

    # First signup
    user = await test_signup_flow()
    if not user:
        print("  Skipping signin test - signup failed")
        return None

    async with httpx.AsyncClient() as client:
        # Sign in
        signin_response = await client.post(
            f"{FRONTEND_URL}/api/auth/sign-in/email",
            json={
                "email": user["email"],
                "password": user["password"],
            }
        )
        print(f"  Signin response: {signin_response.status_code}")
        if signin_response.status_code != 200:
            print(f"  Signin failed: {signin_response.text}")
            return None

        # Get session cookies
        cookies = signin_response.cookies

        # Get JWT token
        token_response = await client.get(
            f"{FRONTEND_URL}/api/auth/token",
            cookies=cookies,
        )
        print(f"  Token response: {token_response.status_code}")
        if token_response.status_code == 200:
            token_data = token_response.json()
            jwt_token = token_data.get("token")
            print(f"  JWT token obtained: {jwt_token[:50] if jwt_token else 'None'}...")
            return {"token": jwt_token, "user": user}
        else:
            print(f"  Token retrieval failed: {token_response.text}")
            return None


async def test_backend_jwt_verification(token_data: dict):
    """Test that backend can verify Better Auth JWT."""
    print("\n=== Testing Backend JWT Verification ===")
    if not token_data or not token_data.get("token"):
        print("  Skipping - no token available")
        return False

    async with httpx.AsyncClient() as client:
        # Try to access a protected endpoint with the JWT
        jwt_token = token_data["token"]
        headers = {"Authorization": f"Bearer {jwt_token}"}

        # Decode token to get user_id (without verification)
        import jwt
        payload = jwt.decode(jwt_token, options={"verify_signature": False})
        user_id = payload.get("sub")
        print(f"  Token user_id: {user_id}")

        # Try to list tasks (protected endpoint)
        response = await client.get(
            f"{BACKEND_URL}/api/{user_id}/tasks",
            headers=headers,
        )
        print(f"  Protected endpoint response: {response.status_code}")
        if response.status_code == 200:
            print("  Backend successfully verified Better Auth JWT!")
            return True
        else:
            print(f"  Verification failed: {response.text}")
            return False


async def run_integration_tests():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("Better Auth JWT Integration Tests")
    print("=" * 60)

    results = {
        "jwks": False,
        "signup": False,
        "signin_token": False,
        "backend_verify": False,
    }

    try:
        # Test JWKS endpoint
        jwks_data = await test_better_auth_jwks()
        results["jwks"] = jwks_data is not None

        # Test signup flow
        user = await test_signup_flow()
        results["signup"] = user is not None

        # Test signin and token
        token_data = await test_signin_and_get_token()
        results["signin_token"] = token_data is not None

        # Test backend verification
        if token_data:
            results["backend_verify"] = await test_backend_jwt_verification(token_data)

    except Exception as e:
        print(f"\nTest error: {e}")

    # Print summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status}")

    all_passed = all(results.values())
    print("\n" + ("ALL TESTS PASSED!" if all_passed else "SOME TESTS FAILED"))
    return all_passed


async def main():
    """Main entry point."""
    manager = ServiceManager()

    try:
        # Start services
        manager.start_frontend()
        manager.start_backend()

        # Wait for services to be ready
        frontend_ready = await wait_for_service(f"{FRONTEND_URL}/api/auth/jwks", "Frontend")
        backend_ready = await wait_for_service(f"{BACKEND_URL}/api/health", "Backend")

        if not frontend_ready or not backend_ready:
            print("Services failed to start. Exiting.")
            sys.exit(1)

        # Run tests
        success = await run_integration_tests()
        sys.exit(0 if success else 1)

    finally:
        manager.stop_all()


if __name__ == "__main__":
    asyncio.run(main())

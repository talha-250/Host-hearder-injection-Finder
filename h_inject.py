import requests
import argparse
import random
from urllib.parse import urlparse
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform color support
init()

def test_host_injection(url_list_file, host_list_file=None, match_codes=None, reflect_check=True):
    """Tests for Host header injection, with optional status code filtering and reflection check."""

    try:
        with open(url_list_file, "r") as url_file:
            urls = [line.strip() for line in url_file]

    except FileNotFoundError:
        print(f"{Fore.RED}Error: URL list file '{url_list_file}' not found.{Style.RESET_ALL}")
        return

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/114.0.1823.82",
        "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
        # Add more as needed...
    ]

    if host_list_file:
        try:
            with open(host_list_file, "r") as f:
                host_headers = [line.strip() for line in f]
        except FileNotFoundError:
            print(f"{Fore.RED}Error: Host list file '{host_list_file}' not found.{Style.RESET_ALL}")
            return
    else:
        host_headers = [
            "example.com",  # Replace with target domain variations
            "evil.com",
            "127.0.0.1",
            "localhost",
            "*.example.com",
            "example.com:8080",
        ]

    if match_codes:
        match_codes = set(map(int, match_codes.split(",")))

    for url in urls:
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            path = parsed_url.path if parsed_url.path else "/"

            for host in host_headers:
                for header_name in ["Host", "X-Forwarded-Host", "Forwarded"]:
                    headers = {
                        header_name: host,
                        "User-Agent": random.choice(user_agents),
                    }

                    try:
                        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)

                        if match_codes is None or response.status_code in match_codes:
                            print(f"URL: {url}")
                            print(f"Header: {header_name}")
                            print(f"Value: {host}")
                            print(f"Status Code: {response.status_code}")
                            #print(f"Response Content: {response.text[:200]}...")  # If you want to see the start of the response
                            print(f"Response Headers: {response.headers}")

                            # Basic checks (customize as needed):
                            if response.status_code == 302 and "evil.com" in response.headers.get("Location", ""):
                                print(f"{Fore.YELLOW}Potential Host Injection: Redirect to evil.com{Style.RESET_ALL}")

                            if reflect_check:
                                if response.status_code == 200 and host in response.text:
                                    print(f"{Fore.GREEN}Potential Host Injection: Host reflected in response{Style.RESET_ALL}")

                            print("-" * 20)

                    except requests.exceptions.RequestException as e:
                        print(f"{Fore.RED}Error for URL '{url}', Header '{header_name}' with value '{host}': {e}{Style.RESET_ALL}")

        except ValueError:
            print(f"{Fore.RED}Invalid URL format: {url}{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test for Host header injection on a list of URLs.")
    parser.add_argument("-U", "--url-list", required=True, help="Path to a file containing a list of URLs.")
    parser.add_argument("-H", "--host-list", help="Path to a file containing a list of Host headers (optional).")
    parser.add_argument("-mc", "--match-codes", help="Comma-separated list of status codes to match (e.g., '200,302').")
    parser.add_argument("--no-reflect", action="store_false", dest="reflect_check", help="Disable host reflection check.")
    args = parser.parse_args()

    test_host_injection(args.url_list, args.host_list, args.match_codes, args.reflect_check)

## Parses Apache logs to derive user browsing behavior.
Input logs have been pre-stripped of IPs and URLs have been pre-hashed to maintain user anonymity.

Example Log:
- - [01/Mar/2022:07:41:28 +0000] "POST /WebTracker/1646121298494:20d2b7c98d32e8:9016:3458c296b3e8227ac7f608f2ac6ecae9f5129ac5ad7c88f61377cb672ebe229dadfda920389590cc5973422d98437c8c461d68ad446155796bfe9a93d6bac1c9:0 HTTP/1.1" 404 5762 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"


usage: webtracker.py [-h] -l FILE

ps aux | grep python | grep --max-count 1 -- --adapter-access-token | grep --only-matching --perl-regexp 'user\s+\d+' | grep --only-matching --perl-regexp '\d+' | clip.exe

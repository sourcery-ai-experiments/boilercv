# Get filepaths
$original_answers_file = '.copier-answers-init.yml'
$original_answers = Get-Content -Delimiter \0 -Path $original_answers_file
$new_answers_file = '.copier-answers.yml'

# Building blocks for two regex replacements
$commit_lookbehind = '(?<=_commit: )'  # (have to use \s instead of \n)
$repo_lookbehind = '(?<=_src_path: )'  # (have to use \s instead of \n)
$match = '\S+'  # anything in-between
$lookahead = '(?=\s)'  # "#]]\n" (have to use \s instead of \n)
# The regexes
$commit = "${commit_lookbehind}${match}${lookahead}"
$repo = "${repo_lookbehind}${match}${lookahead}"
# The replacements
$commit_replacement = 'ff386ef5ab001a54e25d9ffafb6305cad402de7b'
$repo_replacement = 'gh:blakeNaccarato/copier-python'

# Make two replacements in series, then write to file
$new_answers = $original_answers -replace $commit, $commit_replacement
$new_answers = $new_answers -replace $repo, $repo_replacement
$new_answers | Set-Content -NoNewline -Path $new_answers_file

# Clean up
Remove-Item $original_answers_file
Remove-Item 'task.ps1'

# Run copier
copier copy gh:blakeNaccarato/copier-python .

import os, pathlib, re, subprocess, sys, datetime
ROOT = pathlib.Path(__file__).resolve().parent
pw = re.search(r'temporal:\s*(\S+)', pathlib.Path(r'C:\Users\alfonzel\.codex\attachments\7051e76f-5c0e-45ac-b02a-64713544988a\pasted-text.txt').read_text(encoding='utf-8-sig')).group(1)
command = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
script = r'''tmpdir=$(mktemp -d) || exit 1
trap 'rm -f -- "$tmpdir/askpass.sh"; rmdir -- "$tmpdir"' EXIT
trap 'exit 130' INT TERM
cat > "$tmpdir/askpass.sh" <<'HELPER'
#!/bin/sh
printf '%s\n' "$INFRA_PW"
HELPER
chmod 700 "$tmpdir/askpass.sh"
SSH_ASKPASS_REQUIRE=force SSH_ASKPASS="$tmpdir/askpass.sh" ssh -o StrictHostKeyChecking=yes -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=15 -o NumberOfPasswordPrompts=1 alfonzel_opr@10.129.2.165 "$1"
rc=$?
unset INFRA_PW
exit "$rc"
'''
environment = os.environ.copy()
environment['INFRA_PW'] = pw
result = subprocess.run([str(pathlib.Path(os.environ['LOCALAPPDATA'])/'Programs/Git/bin/bash.exe'), '--noprofile', '--norc', '-c', script, 'collect', command], env=environment, capture_output=True, text=True)
environment.pop('INFRA_PW', None)
output = result.stdout.replace(pw, '[REDACTADO]')
errors = result.stderr.replace(pw, '[REDACTADO]')
pw = None
(ROOT/(sys.argv[2]+'.txt')).write_text(output+'\nSTDERR\n'+errors, encoding='utf-8')
print(output)
print(errors)
sys.exit(result.returncode)

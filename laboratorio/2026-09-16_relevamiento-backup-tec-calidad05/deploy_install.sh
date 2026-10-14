sudo -n su -c 'bash -c '"'"'set -euo pipefail
test "$(hostname)" = tec-calidad05
test "$(id -u)" = 0
for p in /var/backups/postgresql/admtech /usr/local/sbin/backup_admtech.sh /etc/cron.d/backup-admtech; do
  if test -e "$p" || test -L "$p"; then printf '"'"'"'"'"'"'"'"'STOP EXISTE %s\n'"'"'"'"'"'"'"'"' "$p"; exit 1; fi
done
free_bytes=$(df -B1 --output=avail /var/backups | tail -n 1)
test "$free_bytes" -ge 5368709120
install -d -o postgres -g postgres -m 0700 /var/backups/postgresql/admtech
restorecon -Rv /var/backups/postgresql
ls -ldZ /var/backups/postgresql /var/backups/postgresql/admtech
namei -om /var/backups/postgresql/admtech
su - postgres -c '"'"'"'"'"'"'"'"'test -w /var/backups/postgresql/admtech && touch /var/backups/postgresql/admtech/.write_test && rm -f /var/backups/postgresql/admtech/.write_test'"'"'"'"'"'"'"'"'
printf '"'"'"'"'"'"'"'"'WRITE_TEST_RC=0\n'"'"'"'"'"'"'"'"'
umask 077
tmp_script=$(mktemp /usr/local/sbin/.backup_admtech.XXXXXXXX)
trap '"'"'"'"'"'"'"'"'rm -f -- "$tmp_script"'"'"'"'"'"'"'"'"' EXIT
printf '"'"'"'"'"'"'"'"'%s'"'"'"'"'"'"'"'"' '"'"'"'"'"'"'"'"'IyEvYmluL2Jhc2gKIyBCYWNrdXAgQURNLVRFQ0ggYXV0b3JpemFkbyAyMDI2LTA5LTE2OyBlamVjdWNpb24gZGlhcmlhIDAyOjMwIGxvY2FsLgojIERlc3Rpbm8gc2VwYXJhZG8gZGUgYmFja3VwX3BnIHBhcmEgY29uc2VydmFyIDMwIGRpYXMgc2luIGxpbXBpZXphIGFqZW5hLgpzZXQgLUVldW8gcGlwZWZhaWwKdW1hc2sgMDc3ClBBVEg9L3Vzci9wZ3NxbC0xMC9iaW46L3Vzci9iaW46L2JpbgpleHBvcnQgUEFUSApyZWFkb25seSBERVNUPS92YXIvYmFja3Vwcy9wb3N0Z3Jlc3FsL2FkbXRlY2gKcmVhZG9ubHkgUEdEVU1QPS91c3IvcGdzcWwtMTAvYmluL3BnX2R1bXAKcmVhZG9ubHkgUEdSRVNUT1JFPS91c3IvcGdzcWwtMTAvYmluL3BnX3Jlc3RvcmUKcmVhZG9ubHkgTUlOX0ZSRUU9NTM2ODcwOTEyMApyZWFkb25seSBSRVRFTlRJT05fTUlOVVRFUz00MzIwMAp0bXA9JycKY2hlY2tzdW1fdG1wPScnCmxvZygpIHsgL3Vzci9iaW4vbG9nZ2VyIC10IGJhY2t1cC1hZG10ZWNoIC0tICIkKiI7IH0KY2xlYW51cCgpIHsKICAgIGxvY2FsIHJjPSQ/CiAgICB0cmFwIC0gRVhJVAogICAgW1sgLXogIiR0bXAiIF1dIHx8IHJtIC1mIC0tICIkdG1wIgogICAgW1sgLXogIiRjaGVja3N1bV90bXAiIF1dIHx8IHJtIC1mIC0tICIkY2hlY2tzdW1fdG1wIgogICAgaWYgKCggcmMgIT0gMCApKTsgdGhlbiBsb2cgIkVSUk9SIGJhY2t1cCBpbmNvbXBsZXRvOyBjb2RpZ289JHJjIiB8fCB0cnVlOyBmaQogICAgZXhpdCAiJHJjIgp9CnRyYXAgY2xlYW51cCBFWElUCnRyYXAgJ2V4aXQgMTMwJyBJTlQKdHJhcCAnZXhpdCAxNDMnIFRFUk0gSFVQCltbICQoaWQgLXVuKSA9PSBwb3N0Z3JlcyBdXSB8fCB7IGxvZyAnRVJST1IgcmVxdWllcmUgdXN1YXJpbyBMaW51eCBwb3N0Z3Jlcyc7IGV4aXQgMTsgfQpbWyAtZCAiJERFU1QiICYmICEgLUwgIiRERVNUIiAmJiAtdyAiJERFU1QiIF1dIHx8IHsgbG9nICdFUlJPUiBkZXN0aW5vIGF1c2VudGUgbyBubyBlc2NyaWJpYmxlJzsgZXhpdCAxOyB9CltbICQoc3RhdCAtYyAlVSAiJERFU1QiKSA9PSBwb3N0Z3JlcyAmJiAkKHN0YXQgLWMgJWEgIiRERVNUIikgPT0gNzAwIF1dIHx8IHsgbG9nICdFUlJPUiBkZXN0aW5vIHJlcXVpZXJlIHByb3BpZXRhcmlvIHBvc3RncmVzIHkgbW9kbyA3MDAnOyBleGl0IDE7IH0KIyBSZXRpcmFyIHZhcmlhYmxlcyBQb3N0Z3JlU1FMIGhlcmVkYWRhczsgYXV0ZW50aWNhY2lvbiBsb2NhbCB2YWxpZGFkYS4KdW5zZXQgUEdQQVNTV09SRCBQR1BBU1NGSUxFIFBHU0VSVklDRSBQR1NFUlZJQ0VGSUxFCnVuc2V0IFBHSE9TVCBQR0hPU1RBRERSIFBHUE9SVCBQR0RBVEFCQVNFIFBHVVNFUiBQR09QVElPTlMKZXhlYyA5PiIkREVTVC8uYmFja3VwX2FkbXRlY2gubG9jayIKaWYgISAvdXNyL2Jpbi9mbG9jayAtbiA5OyB0aGVuIGxvZyAnT01JVElETyBvdHJhIGluc3RhbmNpYSBtYW50aWVuZSBlbCBibG9xdWVvJzsgZXhpdCAxOyBmaQpmcmVlX2J5dGVzPSQoZGYgLUIxIC0tb3V0cHV0PWF2YWlsICIkREVTVCIgfCB0YWlsIC1uIDEpCltbICIkZnJlZV9ieXRlcyIgPX4gXltbOnNwYWNlOl1dKlswLTldK1tbOnNwYWNlOl1dKiQgXV0gfHwgZXhpdCAxCigoIGZyZWVfYnl0ZXMgPj0gTUlOX0ZSRUUgKSkgfHwgeyBsb2cgJ0VSUk9SIG1lbm9zIGRlIDUgR2lCIGRpc3BvbmlibGVzJzsgZXhpdCAxOyB9CnN0YW1wPSQoZGF0ZSAtdSArJVklbSVkVCVIJU0lU1opCm5hbWU9ImFkbXRlY2hfcG9zdGdyZXNfJHtzdGFtcH0uZHVtcCIKW1sgISAtZSAiJERFU1QvJG5hbWUiICYmICEgLWUgIiRERVNULyRuYW1lLnNoYTI1NiIgXV0gfHwgZXhpdCAxCnRtcD0kKG1rdGVtcCAiJERFU1QvLmFkbXRlY2hfZHVtcC5YWFhYWFhYWCIpCmNoZWNrc3VtX3RtcD0kKG1rdGVtcCAiJERFU1QvLmFkbXRlY2hfc2hhMjU2LlhYWFhYWFhYIikKbG9nICJJTklDSU8gYmFzZT1wb3N0Z3JlcyBhcmNoaXZvPSRuYW1lIgoiJFBHRFVNUCIgLS1uby1wYXNzd29yZCAtLXVzZXJuYW1lPXBvc3RncmVzIC0tZGJuYW1lPXBvc3RncmVzIC0tcG9ydD01NDMyIFwKICAgIC0tZm9ybWF0PWN1c3RvbSAtLWNvbXByZXNzPTYgLS1sb2NrLXdhaXQtdGltZW91dD02MHMgLS1maWxlPSIkdG1wIgpbWyAtcyAiJHRtcCIgXV0gfHwgeyBsb2cgJ0VSUk9SIGR1bXAgdmFjaW8nOyBleGl0IDE7IH0KIiRQR1JFU1RPUkUiIC0tbGlzdCAiJHRtcCIgPi9kZXYvbnVsbApkaWdlc3Q9JCgvdXNyL2Jpbi9zaGEyNTZzdW0gIiR0bXAiKQpkaWdlc3Q9JHtkaWdlc3QlJSAqfQpwcmludGYgJyVzICAlc1xuJyAiJGRpZ2VzdCIgIiRuYW1lIiA+ICIkY2hlY2tzdW1fdG1wIgojIENhZGEgYXJjaGl2byBzZSBwdWJsaWNhIGF0w7NtaWNhbWVudGUgZW4gZWwgbWlzbW8gc2lzdGVtYSBkZSBhcmNoaXZvcy4KbXYgLS0gIiR0bXAiICIkREVTVC8kbmFtZSIKdG1wPScnCm12IC0tICIkY2hlY2tzdW1fdG1wIiAiJERFU1QvJG5hbWUuc2hhMjU2IgpjaGVja3N1bV90bXA9JycKKGNkICIkREVTVCIgJiYgL3Vzci9iaW4vc2hhMjU2c3VtIC0tY2hlY2sgLS1zdGF0dXMgIiRuYW1lLnNoYTI1NiIpCiMgTGltcGlhciBzb2xvIHBhcmVzIHByb3Bpb3MsIGRlc3B1w6lzIGRlIHB1YmxpY2FyIHkgdmVyaWZpY2FyIHVuIG51ZXZvIHJlc3BhbGRvLgp3aGlsZSBJRlM9IHJlYWQgLXIgLWQgJycgZXhwaXJlZDsgZG8KICAgIGJhc2U9JHtleHBpcmVkIyMqL30KICAgIFtbICIkYmFzZSIgPX4gXmFkbXRlY2hfcG9zdGdyZXNfWzAtOV17OH1UWzAtOV17Nn1aXC5kdW1wJCBdXSB8fCBjb250aW51ZQogICAgW1sgLWYgIiRleHBpcmVkLnNoYTI1NiIgJiYgISAtTCAiJGV4cGlyZWQuc2hhMjU2IiBdXSB8fCBjb250aW51ZQogICAgcm0gLS0gIiRleHBpcmVkIiAiJGV4cGlyZWQuc2hhMjU2Igpkb25lIDwgPChmaW5kICIkREVTVCIgLW1heGRlcHRoIDEgLXR5cGUgZiAtbmFtZSAnYWRtdGVjaF9wb3N0Z3Jlc18qLmR1bXAnIC1tbWluICsiJFJFVEVOVElPTl9NSU5VVEVTIiAtcHJpbnQwKQpsb2cgIk9LIGJhc2U9cG9zdGdyZXMgYXJjaGl2bz0kbmFtZSBieXRlcz0kKHN0YXQgLWMgJXMgIiRERVNULyRuYW1lIikiCg=='"'"'"'"'"'"'"'"' | base64 -d > "$tmp_script"
bash -n "$tmp_script"
test "$(sha256sum "$tmp_script" | cut -d'"'"'"'"'"'"'"'"' '"'"'"'"'"'"'"'"' -f1)" = '"'"'"'"'"'"'"'"'178f1a52f26ff35ef4e2b1e561cd138749f61ebb34613788eabccffc1459d174'"'"'"'"'"'"'"'"'
chown root:root "$tmp_script"
chmod 0755 "$tmp_script"
mv -n -- "$tmp_script" /usr/local/sbin/backup_admtech.sh
test ! -e "$tmp_script"
bash -n /usr/local/sbin/backup_admtech.sh
ls -lZ /usr/local/sbin/backup_admtech.sh
sha256sum /usr/local/sbin/backup_admtech.sh
su - postgres -c '"'"'"'"'"'"'"'"'test -x /usr/local/sbin/backup_admtech.sh && test ! -w /usr/local/sbin/backup_admtech.sh'"'"'"'"'"'"'"'"'
printf '"'"'"'"'"'"'"'"'SCRIPT_PERMISSIONS_RC=0\n'"'"'"'"'"'"'"'"'
date --iso-8601=seconds
'"'"''

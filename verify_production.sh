#!/usr/bin/env bash
# Run AFTER deploying. Checks live production, as Googlebot would see it.
# Usage: bash verify_production.sh
PREF="https://www.counterculture.online"
ALT="https://counterculture.online"
GB="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
ok(){ printf "  \033[32mPASS\033[0m %s\n" "$1"; }; bad(){ printf "  \033[31mFAIL\033[0m %s\n" "$1"; }

echo "1) Homepage status (as Googlebot)"
c=$(curl -s -o /dev/null -w '%{http_code}' -A "$GB" "$PREF/"); [ "$c" = 200 ] && ok "$PREF/ -> 200" || bad "$PREF/ -> $c"

echo "2) Alternate domain redirects permanently to preferred"
read -r c loc < <(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' "$ALT/")
{ [ "$c" = 301 ] || [ "$c" = 308 ]; } && [ "$loc" = "$PREF/" ] && ok "$ALT/ -> $c -> $loc" || bad "$ALT/ -> $c $loc (want 301/308 to $PREF/)"

echo "3) Metadata present in PRODUCTION HTML"
h=$(curl -s -A "$GB" "$PREF/")
chk(){ echo "$h" | grep -qF "$1" && ok "$2" || bad "$2"; }
chk '<title>COUNTER CULTURE | A Church for the Hungry &amp; Curious</title>' "approved title"
chk 'Something new is happening in Quezon City! COUNTER CULTURE is a new church launching in 2027 near North Ave. and Quezon Ave. Come be part of the story.' "approved description"
chk "rel=\"canonical\" href=\"$PREF/\"" "canonical -> $PREF/"
chk 'og:site_name" content="COUNTER CULTURE"' "og:site_name"
chk '"@type": "WebSite"' "WebSite JSON-LD"
chk '"legalName": "COUNTER CULTURE CHURCH INC."' "Organization legalName"
n=$(echo "$h" | grep -o 'name="description"' | wc -l); [ "$n" = 1 ] && ok "exactly 1 meta description" || bad "meta descriptions: $n"
echo "$h" | grep -qi 'noindex' && bad "noindex found" || ok "no noindex"

echo "4) Favicons (as Googlebot)"
for f in favicon.ico favicon-48x48.png favicon-96x96.png apple-touch-icon.png logo.png; do
  c=$(curl -s -o /dev/null -w '%{http_code}' -A "$GB" "$PREF/$f"); [ "$c" = 200 ] && ok "/$f -> 200" || bad "/$f -> $c"
done

echo "5) robots.txt + sitemap"
r=$(curl -s -A "$GB" "$PREF/robots.txt"); echo "$r" | grep -qiE '^Disallow: */ *$' && bad "robots.txt blocks everything" || ok "robots.txt does not block /"
echo "$r" | grep -qi "sitemap: $PREF/sitemap.xml" && ok "robots.txt lists sitemap" || bad "robots.txt missing Sitemap line"
c=$(curl -s -o /dev/null -w '%{http_code}' "$PREF/sitemap.xml"); [ "$c" = 200 ] && ok "sitemap.xml -> 200" || bad "sitemap.xml -> $c"
curl -s "$PREF/sitemap.xml" | grep -qF "<loc>$PREF/</loc>" && ok "sitemap contains homepage" || bad "sitemap missing homepage"

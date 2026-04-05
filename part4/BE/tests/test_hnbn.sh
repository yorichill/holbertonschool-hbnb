#!/bin/bash

BASE="http://127.0.0.1:5000/api/v1"
PASS=0
FAIL=0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check() {
  local id="$1"
  local desc="$2"
  local expected="$3"
  local actual="$4"

  if [ "$actual" == "$expected" ]; then
    echo -e "${GREEN}✅ [$id]${NC} $desc → $actual"
    PASS=$((PASS+1))
  else
    echo -e "${RED}❌ [$id]${NC} $desc → attendu $expected, reçu $actual"
    FAIL=$((FAIL+1))
  fi
}

section() {
  echo ""
  echo -e "${BLUE}══════════════════════════════════════${NC}"
  echo -e "${YELLOW}  $1${NC}"
  echo -e "${BLUE}══════════════════════════════════════${NC}"
}

# ── Helper: extrait un champ JSON ──────────────────────────────────────────
json_get() {
  echo "$1" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('$2',''))" 2>/dev/null
}

# ═══════════════════════════════════════════════════════════════════════════
section "1. AUTH"
# ═══════════════════════════════════════════════════════════════════════════

# 1.1 Login admin OK
R=$(curl -s -o /tmp/body -w "%{http_code}" -X POST "$BASE/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@hbnb.io","password":"admin1234"}')
check "1.1" "Login admin valide" "200" "$R"
TOKEN_ADMIN=$(python3 -c "import json; d=json.load(open('/tmp/body')); print(d.get('access_token',''))" 2>/dev/null)

# 1.2 Protected avec token admin
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/auth/protected" \
  -H "Authorization: $TOKEN_ADMIN")
check "1.2" "GET /auth/protected avec token" "200" "$R"

# 1.3 Login mauvais mot de passe
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@hbnb.io","password":"wrong"}')
check "1.3" "Login mauvais mot de passe" "401" "$R"

# ═══════════════════════════════════════════════════════════════════════════
section "2. USERS"
# ═══════════════════════════════════════════════════════════════════════════

# 2.1 Créer Alice
R=$(curl -s -o /tmp/body -w "%{http_code}" -X POST "$BASE/users/" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Alice","last_name":"Dupont","email":"alice@example.com","password":"alice1234"}')
check "2.1" "Créer Alice" "201" "$R"
ALICE_ID=$(python3 -c "import json; d=json.load(open('/tmp/body')); print(d.get('id',''))" 2>/dev/null)

# 2.2 Créer Bob
R=$(curl -s -o /tmp/body -w "%{http_code}" -X POST "$BASE/users/" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Bob","last_name":"Martin","email":"bob@example.com","password":"bob1234"}')
check "2.2" "Créer Bob" "201" "$R"
BOB_ID=$(python3 -c "import json; d=json.load(open('/tmp/body')); print(d.get('id',''))" 2>/dev/null)

# 2.3 Email déjà utilisé
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/users/" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Alice","last_name":"Dupont","email":"alice@example.com","password":"alice1234"}')
check "2.3" "Email déjà utilisé" "400" "$R"

# 2.4 Lister users
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/users/")
check "2.4" "Lister tous les users" "200" "$R"

# 2.5 Détail user
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/users/$ALICE_ID")
check "2.5" "Détail Alice" "200" "$R"

# Login Alice
TOKEN_ALICE=$(curl -s -X POST "$BASE/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","password":"alice1234"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

# Login Bob
TOKEN_BOB=$(curl -s -X POST "$BASE/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"bob@example.com","password":"bob1234"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

# 2.6 Alice modifie son profil
R=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$BASE/users/$ALICE_ID" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_ALICE" \
  -d '{"first_name":"Alice","last_name":"Dupont-Updated"}')
check "2.6" "Alice modifie son profil" "200" "$R"

# 2.7 Alice modifie Bob → 403
R=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$BASE/users/$BOB_ID" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_ALICE" \
  -d '{"first_name":"Hacked"}')
check "2.7" "Alice modifie Bob (403)" "403" "$R"

# 2.8 Admin donne is_admin à Alice
R=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$BASE/users/$ALICE_ID/admin" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_ADMIN" \
  -d '{"is_admin":true}')
check "2.8" "Admin → Alice is_admin:true" "200" "$R"

# ═══════════════════════════════════════════════════════════════════════════
section "3. AMENITIES"
# ═══════════════════════════════════════════════════════════════════════════

# 3.1 Lister amenities
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/amenities/")
check "3.1" "Lister amenities (seed)" "200" "$R"

# 3.2 Admin crée Jacuzzi
R=$(curl -s -o /tmp/body -w "%{http_code}" -X POST "$BASE/amenities/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_ADMIN" \
  -d '{"name":"Jacuzzi"}')
check "3.2" "Admin crée Jacuzzi" "201" "$R"
AMENITY_ID=$(python3 -c "import json; d=json.load(open('/tmp/body')); print(d.get('id',''))" 2>/dev/null)

# 3.3 Alice (non admin au départ) crée amenity → 403
# On recrée un token Alice sans admin pour ce test
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/amenities/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_BOB" \
  -d '{"name":"Sauna"}')
check "3.3" "Bob (non admin) crée amenity (403)" "403" "$R"

# 3.4 Détail amenity
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/amenities/$AMENITY_ID")
check "3.4" "Détail amenity" "200" "$R"

# ═══════════════════════════════════════════════════════════════════════════
section "4. PLACES"
# ═══════════════════════════════════════════════════════════════════════════

# 4.1 Bob crée un place
R=$(curl -s -o /tmp/body -w "%{http_code}" -X POST "$BASE/places/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_BOB" \
  -d '{"title":"Cozy Paris Apt","description":"A nice place","price":120,"latitude":48.8566,"longitude":2.3522}')
check "4.1" "Bob crée un place" "201" "$R"
PLACE_ID=$(python3 -c "import json; d=json.load(open('/tmp/body')); print(d.get('id',''))" 2>/dev/null)

# 4.2 Créer place sans token → 401
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/places/" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Test","price":50,"latitude":48.0,"longitude":2.0}')
check "4.2" "Créer place sans token (401)" "401" "$R"

# 4.3 Lister places
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/places/")
check "4.3" "Lister tous les places" "200" "$R"

# 4.4 Détail place
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/places/$PLACE_ID")
check "4.4" "Détail place (reviews embarquées)" "200" "$R"

# 4.5 Bob update son place
R=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$BASE/places/$PLACE_ID" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_BOB" \
  -d '{"title":"Cozy Paris Apt Updated","price":150}')
check "4.5" "Bob update son place" "200" "$R"

# 4.6 Alice update le place de Bob → 403
R=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$BASE/places/$PLACE_ID" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_ALICE" \
  -d '{"title":"Hacked"}')
check "4.6" "Alice update place de Bob (403)" "403" "$R"

# ═══════════════════════════════════════════════════════════════════════════
section "5. REVIEWS"
# ═══════════════════════════════════════════════════════════════════════════

# 5.1 Alice review le place de Bob
R=$(curl -s -o /tmp/body -w "%{http_code}" -X POST "$BASE/places/$PLACE_ID/reviews" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_ALICE" \
  -d '{"rating":5,"text":"Amazing place!"}')
check "5.1" "Alice review le place de Bob" "201" "$R"
REVIEW_ID=$(python3 -c "import json; d=json.load(open('/tmp/body')); print(d.get('id',''))" 2>/dev/null)

# 5.2 Bob review son propre place → 400
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/places/$PLACE_ID/reviews" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_BOB" \
  -d '{"rating":4,"text":"My own place!"}')
check "5.2" "Bob review son propre place (400)" "400" "$R"

# 5.3 Alice 2e review → 400
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/places/$PLACE_ID/reviews" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_ALICE" \
  -d '{"rating":3,"text":"Second review!"}')
check "5.3" "Alice 2e review (400)" "400" "$R"

# 5.4 Lister reviews du place
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/places/$PLACE_ID/reviews")
check "5.4" "Lister reviews du place" "200" "$R"

# 5.5 Détail review
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/reviews/$REVIEW_ID")
check "5.5" "Détail review" "200" "$R"

# 5.6 Alice modifie sa review
R=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$BASE/reviews/$REVIEW_ID" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_ALICE" \
  -d '{"rating":4,"text":"Updated review!"}')
check "5.6" "Alice modifie sa review" "200" "$R"

# 5.7 Bob modifie la review d'Alice → 403
R=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$BASE/reviews/$REVIEW_ID" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_BOB" \
  -d '{"rating":1,"text":"Hacked!"}')
check "5.7" "Bob modifie review Alice (403)" "403" "$R"

# 5.8 Reviews visibles dans GET place
R=$(curl -s -o /tmp/body -w "%{http_code}" -X GET "$BASE/places/$PLACE_ID")
REVIEWS=$(python3 -c "import json; d=json.load(open('/tmp/body')); print(len(d.get('reviews',[])))" 2>/dev/null)
check "5.8" "Reviews dans GET place" "200" "$R"
[ "$REVIEWS" -gt 0 ] && echo -e "   ${GREEN}→ $REVIEWS review(s) embarquée(s) ✓${NC}" || echo -e "   ${RED}→ reviews vides dans la réponse !${NC}"

# 5.9 Alice supprime sa review
R=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE/reviews/$REVIEW_ID" \
  -H "Authorization: $TOKEN_ALICE")
check "5.9" "Alice supprime sa review" "200" "$R"

# ═══════════════════════════════════════════════════════════════════════════
section "6. BOOKINGS"
# ═══════════════════════════════════════════════════════════════════════════

# 6.1 Bob réserve
R=$(curl -s -o /tmp/body -w "%{http_code}" -X POST "$BASE/bookings/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_BOB" \
  -d "{\"place_id\":\"$PLACE_ID\",\"user_id\":\"$BOB_ID\",\"check_in\":\"2026-07-01\",\"check_out\":\"2026-07-05\"}")
check "6.1" "Bob réserve 2026-07-01→07-05" "201" "$R"
BOOKING_ID=$(python3 -c "import json; d=json.load(open('/tmp/body')); print(d.get('id',''))" 2>/dev/null)

# 6.2 Dates qui chevauchent → 409
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/bookings/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_ALICE" \
  -d "{\"place_id\":\"$PLACE_ID\",\"user_id\":\"$ALICE_ID\",\"check_in\":\"2026-07-02\",\"check_out\":\"2026-07-06\"}")
check "6.2" "Dates chevauchantes (409)" "409" "$R"

# 6.3 check_in dans le passé → 400
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/bookings/" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_BOB" \
  -d "{\"place_id\":\"$PLACE_ID\",\"user_id\":\"$BOB_ID\",\"check_in\":\"2020-01-01\",\"check_out\":\"2020-01-05\"}")

# 6.4 Bob lit sa booking
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/bookings/$BOOKING_ID" \
  -H "Authorization: $TOKEN_BOB")
check "6.4" "Bob lit sa booking" "200" "$R"

# 6.5 Alice lit la booking de Bob → 403
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/bookings/$BOOKING_ID" \
  -H "Authorization: $TOKEN_ALICE")
check "6.5" "Alice lit booking de Bob (403)" "403" "$R"

# 6.6 Confirmer booking
R=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$BASE/bookings/$BOOKING_ID/status" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_ADMIN" \
  -d '{"status":"confirmed"}')
check "6.6" "Status: confirmed" "200" "$R"

# 6.7 Re-confirmer → 400
R=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$BASE/bookings/$BOOKING_ID/status" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_ADMIN" \
  -d '{"status":"confirmed"}')
check "6.7" "Re-confirmer déjà confirmé (400)" "400" "$R"

# 6.8 Annuler booking
R=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$BASE/bookings/$BOOKING_ID/status" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $TOKEN_ADMIN" \
  -d '{"status":"cancelled"}')
check "6.8" "Status: cancelled" "200" "$R"

# 6.9 Bookings de Bob
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/bookings/users/$BOB_ID" \
  -H "Authorization: $TOKEN_BOB")
check "6.9" "Bookings de Bob" "200" "$R"

# 6.10 Bookings du place (owner)
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/bookings/places/$PLACE_ID" \
  -H "Authorization: $TOKEN_BOB")
check "6.10" "Bookings du place (owner Bob)" "200" "$R"

# 6.11 Admin liste complète
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/bookings/" \
  -H "Authorization: $TOKEN_ADMIN")
check "6.11" "Admin liste toutes les bookings" "200" "$R"

# 6.12 Bob liste complète → 403
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/bookings/" \
  -H "Authorization: $TOKEN_BOB")
check "6.12" "Bob liste complète (403)" "403" "$R"

# ═══════════════════════════════════════════════════════════════════════════
section "7. SUPPRESSION"
# ═══════════════════════════════════════════════════════════════════════════

# 7.1 Bob supprime son place
R=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE/places/$PLACE_ID" \
  -H "Authorization: $TOKEN_BOB")
check "7.1" "Bob supprime son place" "200" "$R"

# 7.2 Vérification suppression → 404
R=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE/places/$PLACE_ID")
check "7.2" "Place supprimé (404)" "404" "$R"

# ═══════════════════════════════════════════════════════════════════════════
section "RÉSULTAT FINAL"
# ═══════════════════════════════════════════════════════════════════════════
TOTAL=$((PASS+FAIL))
echo ""
echo -e "  ${GREEN}✅ Réussis : $PASS / $TOTAL${NC}"
echo -e "  ${RED}❌ Échoués : $FAIL / $TOTAL${NC}"
echo ""
if [ $FAIL -eq 0 ]; then
  echo -e "  ${GREEN}🎉 Tous les tests passent !${NC}"
else
  echo -e "  ${YELLOW}⚠️  $FAIL test(s) à corriger.${NC}"
fi
echo ""
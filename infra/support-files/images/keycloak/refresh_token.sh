#!/bin/bash
get_client_id(){
    echo $1 | \
    sed 's/^\[ *//;s/ *\]$//' | \
    tr ',' '\n' | \
    grep -B1 "\"clientId\" *: *\"$2\"" | \
    grep '"id"' | \
    sed 's/.*"id" *: *"\([^"]*\)".*/\1/'
}
/opt/keycloak/bin/kcadm.sh config credentials --server "$KC_HOSTNAME" --realm master --user "$KC_BOOTSTRAP_ADMIN_USERNAME" --password "$KC_BOOTSTRAP_ADMIN_PASSWORD"

CLIENT_JSON=$(/opt/keycloak/bin/kcadm.sh get clients -r lite --fields id,clientId,publicClient)
CLIENT_ID=$(get_client_id "$CLIENT_JSON" "$1")
/opt/keycloak/bin/kcadm.sh create "clients/$CLIENT_ID/client-secret" -r "lite"
/opt/keycloak/bin/kcadm.sh get "clients/$CLIENT_ID/client-secret" -r "lite" 
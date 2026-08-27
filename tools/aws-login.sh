#!/usr/bin/env bash
# Get a working AWS session, then prove it works. Bash/Git-Bash twin of aws-login.ps1.
#
#   source tools/aws-login.sh           # login if needed. SOURCE it, so AWS_PROFILE sticks.
#   source tools/aws-login.sh --force   # re-login (picks up new IAM grants)
#   source tools/aws-login.sh --check   # run the permission probe afterwards
#
# Source rather than execute: a subshell would export AWS_PROFILE and then throw it away.
#
# Re-login is how a permission-set change takes effect. SSO bakes grants into the role
# session, so a new IAM policy does nothing until the session is reissued. If IT says "done"
# and you still get AccessDenied, --force is the fix.

PROFILE_NAME="genesis"
FORCE=0
CHECK=0
for arg in "$@"; do
    case "$arg" in
        --force) FORCE=1 ;;
        --check) CHECK=1 ;;
        --profile=*) PROFILE_NAME="${arg#*=}" ;;
    esac
done

# The CLI is missing from the PATH of shells opened before it was installed.
AWS_BIN="$(command -v aws 2>/dev/null)"
for c in "/c/Program Files/Amazon/AWSCLIV2/aws.exe" \
         "/c/Program Files (x86)/Amazon/AWSCLIV2/aws.exe" \
         "$LOCALAPPDATA/Programs/AWSCLIV2/aws.exe"; do
    [ -n "$AWS_BIN" ] && break
    [ -x "$c" ] && AWS_BIN="$c"
done
if [ -z "$AWS_BIN" ]; then
    echo "AWS CLI v2 not found. v1 cannot do SSO login." >&2
    return 1 2>/dev/null || exit 1
fi

VERSION="$("$AWS_BIN" --version 2>&1)"
echo "CLI      $VERSION"
case "$VERSION" in
    *aws-cli/2.*) ;;
    *) echo "Need CLI v2, found: $VERSION" >&2; return 1 2>/dev/null || exit 1 ;;
esac

# A static key in the environment silently outranks the SSO profile.
for v in AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN; do
    if [ -n "$(printenv "$v" 2>/dev/null)" ]; then
        echo "WARNING: $v is set and outranks the '$PROFILE_NAME' profile. Unsetting for this shell."
        unset "$v"
    fi
done

export AWS_PROFILE="$PROFILE_NAME"

_whoami() { "$AWS_BIN" sts get-caller-identity --profile "$PROFILE_NAME" --output json 2>/dev/null; }

WHO=""
[ "$FORCE" -eq 0 ] && WHO="$(_whoami)"

if ! echo "$WHO" | grep -q '"Arn"'; then
    [ "$FORCE" -eq 1 ] && echo "" && echo "--force: re-logging in to pick up new IAM grants..." \
                       || { echo ""; echo "No valid session. Logging in..."; }
    echo "A browser will open. Approve the request there."
    echo ""
    "$AWS_BIN" sso login --profile "$PROFILE_NAME" || {
        echo "sso login failed. Check sso_start_url in ~/.aws/config." >&2
        return 1 2>/dev/null || exit 1
    }
    WHO="$(_whoami)"
    if ! echo "$WHO" | grep -q '"Arn"'; then
        echo "Logged in but credentials do not resolve. Check sso_account_id / sso_role_name." >&2
        return 1 2>/dev/null || exit 1
    fi
fi

ARN="$(echo "$WHO" | grep -oE '"Arn": *"[^"]+"' | cut -d'"' -f4)"
ACCT="$(echo "$WHO" | grep -oE '"Account": *"[^"]+"' | cut -d'"' -f4)"
REGION="$("$AWS_BIN" configure get region --profile "$PROFILE_NAME" 2>/dev/null)"

echo ""
echo "Account  $ACCT"
echo "Identity $ARN"
echo "Region   $REGION"
case "$ARN" in
    *assumed-role/AWSReservedSSO*) ;;
    *) echo "WARNING: not an SSO role session; a static credential may be winning." ;;
esac
[ "$REGION" = "us-east-1" ] || echo "WARNING: expected us-east-1 (model ARNs and costs assume it)."

echo ""
echo "Ready. AWS_PROFILE=$PROFILE_NAME is set for this shell."

if [ "$CHECK" -eq 1 ]; then
    echo ""
    uv run --with boto3 python tools/aws_probe.py
else
    echo "Next: source tools/aws-login.sh --check   (verifies every permission the build needs)"
fi

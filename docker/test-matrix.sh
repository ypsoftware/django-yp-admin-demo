#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

declare -a MATRIX=(
  "3.11 4.2"
  "3.12 4.2"
  "3.12 5.2"
  "3.13 5.2"
  "3.13 6.0"
  "3.14 6.0"
)

YP_VER="${YP_ADMIN_VERSION:-0.1.0a3}"
declare -a RESULTS=()

for combo in "${MATRIX[@]}"; do
  read py dj <<< "$combo"
  tag="yp-demo-py${py}-dj${dj}"
  echo
  echo "=========================================="
  echo "Building Python ${py} + Django ${dj}"
  echo "=========================================="
  if docker build \
      -f docker/Dockerfile \
      --build-arg PYTHON_VERSION="${py}" \
      --build-arg DJANGO_VERSION="${dj}" \
      --build-arg YP_ADMIN_VERSION="${YP_VER}" \
      -t "${tag}" \
      .; then
    RESULTS+=("PASS  py${py} dj${dj}")
  else
    RESULTS+=("FAIL  py${py} dj${dj}")
  fi
done

echo
echo "=========================================="
echo "Matrix summary:"
for r in "${RESULTS[@]}"; do
  echo "  $r"
done
echo "=========================================="

# Exit non-zero if any failed
for r in "${RESULTS[@]}"; do
  case "$r" in FAIL*) exit 1 ;; esac
done

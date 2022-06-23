#!/bin/bash
# More safety, by turning some bugs into errors.
# Without `errexit` you don’t need ! and can replace
# ${PIPESTATUS[0]} with a simple $?, but I prefer safety.
set -o errexit -o pipefail -o noclobber -o nounset

version=$1

poetry version $version
git commit pyproject.yaml -m "feat: $version"
git tag $version
git push --tags
git push
poetry publish --build
gh release create $version

param ([String][Parameter(Mandatory)] $version)

poetry version $version
git commit pyproject.yaml -m "feat: $version"
git tag $version
git push --tags
git push
poetry publish --build
gh release create $version

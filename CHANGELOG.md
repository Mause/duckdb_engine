# Changelog

## [0.3.4](https://github.com/Mause/duckdb_engine/compare/v0.3.3...v0.3.4) (2022-08-12)


### Bug Fixes

* disable comments in dialect ([96cca1c](https://github.com/Mause/duckdb_engine/commit/96cca1c6bd4c10a0c8f70fbd695fa8434c94358f))
* restore mypy checking to github builds ([b252679](https://github.com/Mause/duckdb_engine/commit/b252679ed4da3477cd39bd37825639f03d5ded5a))

## [0.3.3](https://github.com/Mause/duckdb_engine/compare/v0.3.2...v0.3.3) (2022-08-06)


### Bug Fixes

* add code coverage reporting ([019b61c](https://github.com/Mause/duckdb_engine/commit/019b61ca21a9f47467b2f01acdecf275fe658aec))
* add documentation and test for duckdb config ([f3e577a](https://github.com/Mause/duckdb_engine/commit/f3e577a8fcdd9b00db0e0ea8002bc3d574003e02))
* correct dialect error lookup for bleeding edge ([0e04d02](https://github.com/Mause/duckdb_engine/commit/0e04d02d86c4f3e8d4ff3cf8d147e0707faedff9))

## [0.3.2](https://github.com/Mause/duckdb_engine/compare/v0.3.1...v0.3.2) (2022-08-05)


### Bug Fixes

* unpin numpy for python 3.6 ([3e87509](https://github.com/Mause/duckdb_engine/commit/3e875091164c018db6ccfa4e1dd2fd5e6238979c))

## [0.3.1](https://github.com/Mause/duckdb_engine/compare/v0.3.0...v0.3.1) (2022-08-05)


### Bug Fixes

* add py.typed file ([99e39e4](https://github.com/Mause/duckdb_engine/commit/99e39e4184d3ec5a48cf1eac65641035f5fb79a8))
* update test for bleeding edge ([ec63594](https://github.com/Mause/duckdb_engine/commit/ec63594dbe99c58ac88870de8d3daea847970302))

## [0.3.0](https://github.com/Mause/duckdb_engine/compare/v0.2.0...v0.3.0) (2022-08-02)


### Features

* use SingletonThreadPool for :memory: connections ([58ef77a](https://github.com/Mause/duckdb_engine/commit/58ef77acb55f3bfbe8be511f79a151a25f54a374))

## [0.2.0](https://github.com/Mause/duckdb_engine/compare/v0.1.12...v0.2.0) (2022-07-03)


### Features

* add missing apilevel and threadsafety attributes on duckdb DBAPI ([bc413a3](https://github.com/Mause/duckdb_engine/commit/bc413a3df1579f32dbff48069da8ae338f21854c))
* add release-please config ([6e9a2d7](https://github.com/Mause/duckdb_engine/commit/6e9a2d70ae666f6c488afa984f72b8a8a1528f75))
* add support for Binary ([8235377](https://github.com/Mause/duckdb_engine/commit/82353778ab8c50804e42b21049eb58c626c51b8f))
* enable relationship integrity ([f41bd10](https://github.com/Mause/duckdb_engine/commit/f41bd1030c0c9e5406ff76da7f9a3ef716c311c7))
* improve release script ([bcb17bf](https://github.com/Mause/duckdb_engine/commit/bcb17bf05667b539e56fa83ece9bdf57dde9918a))
* override driver name ([1a7bb4e](https://github.com/Mause/duckdb_engine/commit/1a7bb4e4b558dac6bf5f0e07d697789b1f83b0dc))
* strip comments from generated sql ([66265a2](https://github.com/Mause/duckdb_engine/commit/66265a2a0755fabb7d2e847d5a75ac182fc81714))
* warn when we find comments in the ddl ([5b27a7f](https://github.com/Mause/duckdb_engine/commit/5b27a7f374bf58023629c0576b85ae4323ec5fb2))


### Bug Fixes

* enable updating of existing models ([14a4d5f](https://github.com/Mause/duckdb_engine/commit/14a4d5f68ed60e4fa81c9ba60c1c906ffb538998))

## [0.1.12a0](https://github.com/Mause/duckdb_engine/compare/v0.1.11...v0.1.12a0) (2022-06-23)


### Features
* feat: enable interval support by @Mause in https://github.com/Mause/duckdb_engine/pull/278
* fix: use modern dialect registration by @Mause in https://github.com/Mause/duckdb_engine/pull/280

### Chores
* chore: add release script by @Mause in https://github.com/Mause/duckdb_engine/pull/276
* Update and rename release.ps1 to release.sh by @Mause in https://github.com/Mause/duckdb_engine/pull/287
* feat: add duckdb_version test decorator by @Mause in https://github.com/Mause/duckdb_engine/pull/272
* chore: add links to bug tracker and changelog by @Mause in https://github.com/Mause/duckdb_engine/pull/282
* feature/bug report template by @Mause in https://github.com/Mause/duckdb_engine/pull/285
* feat: Create CODE_OF_CONDUCT.md by @Mause in https://github.com/Mause/duckdb_engine/pull/284

### Version bumps
* chore(deps): bump duckdb from 0.3.4 to 0.4.0 by @dependabot in https://github.com/Mause/duckdb_engine/pull/273
* chore(deps): update github/codeql-action action to v1.1.13 by @renovate in https://github.com/Mause/duckdb_engine/pull/279
* chore(deps): update github/codeql-action action to v1.1.14 by @renovate in https://github.com/Mause/duckdb_engine/pull/286

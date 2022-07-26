# Changelog

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

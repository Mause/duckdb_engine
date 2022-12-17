# Changelog

## [0.6.6](https://github.com/Mause/duckdb_engine/compare/v0.6.5...v0.6.6) (2022-12-17)


### Bug Fixes

* add missing data types ([92cef1b](https://github.com/Mause/duckdb_engine/commit/92cef1bf8f7fb12786675c450f8d134f9ed9104b))
* add missing integer data types ([c7e9ccf](https://github.com/Mause/duckdb_engine/commit/c7e9ccf70a3f6baeca40909e18dfc628fa2401b1))
* disable server side cursors ([bae0a1c](https://github.com/Mause/duckdb_engine/commit/bae0a1c23879fac3d6bf910979a2923531128f83))

## [0.6.5](https://github.com/Mause/duckdb_engine/compare/v0.6.4...v0.6.5) (2022-11-22)


### ⚠ BREAKING CHANGES

* drop python 3.6 support

### Documentation

* add note regarding fetchmany support in duckdb=&gt;0.5.0 ([7ccbaa9](https://github.com/Mause/duckdb_engine/commit/7ccbaa9873d14a21e2fb54a20931c29fe991b370))


### Dependencies

* add snapshottest ([0b18f47](https://github.com/Mause/duckdb_engine/commit/0b18f47b43fd5e34689a555b6f7706fbe6162d21))
* bump tested duckdb to 0.5.1 in tox.ini ([da71828](https://github.com/Mause/duckdb_engine/commit/da718286e99be27f754ddc467d2b9bc137e88f8a))
* declare shared test dependencies ([e43823c](https://github.com/Mause/duckdb_engine/commit/e43823ca29c9c75772612bf59812335ddb721790))
* fix requirement declaration ([e3923ee](https://github.com/Mause/duckdb_engine/commit/e3923ee693a2bba455708787666652985b972b9f))
* test against 0.5.1 ([0aca52e](https://github.com/Mause/duckdb_engine/commit/0aca52e21f2f2d4d2e5e847b5002a715b83dd5d2))


### Code Refactoring

* drop python 3.6 support ([0d81998](https://github.com/Mause/duckdb_engine/commit/0d81998caafee51d86f1692cd73867561b0ce576))


### Miscellaneous Chores

* release 0.6.5 ([52eca6f](https://github.com/Mause/duckdb_engine/commit/52eca6fce78319893dd6ba9de1e193d920e03c78))

## [0.6.4](https://github.com/Mause/duckdb_engine/compare/v0.6.3...v0.6.4) (2022-09-11)


### Bug Fixes

* stub out Dialect#get_indexes for now ([1d450ab](https://github.com/Mause/duckdb_engine/commit/1d450abd21afeff61f355ac2b94b0d7d80adac36))
* use real fetchmany now it's available ([06400b4](https://github.com/Mause/duckdb_engine/commit/06400b464c100dedf43960b9e89470f8f53b7f70))


### Dependencies

* bump locked duckdb version ([1a83643](https://github.com/Mause/duckdb_engine/commit/1a8364309ee89db614d3dd7caafda5ba1ca51786))

## [0.6.3](https://github.com/Mause/duckdb_engine/compare/v0.6.2...v0.6.3) (2022-09-08)


### Bug Fixes

* add schema support to get_view_names ([b58bf32](https://github.com/Mause/duckdb_engine/commit/b58bf3234b77e26871fb4373358d4b55627eae8b))
* correct get_view_names for older sqlalchemy ([b58bf32](https://github.com/Mause/duckdb_engine/commit/b58bf3234b77e26871fb4373358d4b55627eae8b))
* repin duckdb & poetry ([#400](https://github.com/Mause/duckdb_engine/issues/400)) ([4586852](https://github.com/Mause/duckdb_engine/commit/4586852eae2b49241e32b02a40d16eefa7d809c1))

## [0.6.2](https://github.com/Mause/duckdb_engine/compare/v0.6.1...v0.6.2) (2022-08-25)


### Bug Fixes

* fix bleeding edge duckdb for exceptions changes ([f955264](https://github.com/Mause/duckdb_engine/commit/f9552642fe212d114a3670068dc73243594a0cec))

## [0.6.1](https://github.com/Mause/duckdb_engine/compare/v0.6.0...v0.6.1) (2022-08-23)


### Bug Fixes

* support boolean and integer config values ([4a2c639](https://github.com/Mause/duckdb_engine/commit/4a2c6399175fc35e071319b193f3b5de0c3c0878))

## [0.6.0](https://github.com/Mause/duckdb_engine/compare/v0.5.0...v0.6.0) (2022-08-21)


### Features

* allow preloading of extensions ([13a92e1](https://github.com/Mause/duckdb_engine/commit/13a92e1fa7d6bdb5777b46c234cb00a150978e9c))


### Documentation

* document preload_extensions config parameter ([c0f2a99](https://github.com/Mause/duckdb_engine/commit/c0f2a993ee826fa91cab2add7321c52e437bb5a8))
* link to example of IPython-SQL usage ([96e8bdf](https://github.com/Mause/duckdb_engine/commit/96e8bdf3aa8e0d645534bd19188d086d234e606e))

## [0.5.0](https://github.com/Mause/duckdb_engine/compare/v0.4.0...v0.5.0) (2022-08-19)


### Features

* support unsigned integer types ([a69a35b](https://github.com/Mause/duckdb_engine/commit/a69a35bdfbfc9b992bc31dfb0f31f1097458d741))


### Bug Fixes

* try to fix poetry installation in workflow ([db21892](https://github.com/Mause/duckdb_engine/commit/db2189296782ecee0c83d9b2e8a91f6a4c0dd3bb))


### Documentation

* mention unsigned integer support in README ([4e403cb](https://github.com/Mause/duckdb_engine/commit/4e403cb89c32031c5966725427d14162b4ceceab))

## [0.4.0](https://github.com/Mause/duckdb_engine/compare/v0.3.4...v0.4.0) (2022-08-15)


### Features

* switch to first party sqlalchemy stubs ([cf9f626](https://github.com/Mause/duckdb_engine/commit/cf9f6268bc1da8418e7188e37fe6c0c20cb2a05e))


### Bug Fixes

* support ping on latest sqlalchemy ([bd63122](https://github.com/Mause/duckdb_engine/commit/bd631226f03f28c5fa2532b9ddd20a69c70a49e0))

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

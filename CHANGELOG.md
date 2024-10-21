# Changelog

## [0.13.4](https://github.com/Mause/duckdb_engine/compare/v0.13.3...v0.13.4) (2024-10-21)


### Bug Fixes

* **deps:** update dependency duckdb to v1.1.2 ([d363897](https://github.com/Mause/duckdb_engine/commit/d363897bc63bb7814f48e454d2afc3c633073205))

## [0.13.3](https://github.com/Mause/duckdb_engine/compare/v0.13.2...v0.13.3) (2024-10-21)


### Bug Fixes

* add varint type ([220c18f](https://github.com/Mause/duckdb_engine/commit/220c18f310d113bbfffa9c82379eca6c7cf7f95b))
* restrict varint to supported versions ([ccdbc06](https://github.com/Mause/duckdb_engine/commit/ccdbc06c7fd07eba02e91cecdefe54b4ea6ea44b))
* update Map type for 1.0+ ([7574837](https://github.com/Mause/duckdb_engine/commit/757483786a1eba7a606de90c665dcd86dd00dcec))

## [0.13.2](https://github.com/Mause/duckdb_engine/compare/v0.13.1...v0.13.2) (2024-09-04)


### Bug Fixes

* **get_view_names:** Use proper schema ([#1082](https://github.com/Mause/duckdb_engine/issues/1082)) ([d5319c8](https://github.com/Mause/duckdb_engine/commit/d5319c80d3883425734062640ebd8562cf8525fb))


### Documentation

* use `read_only=False` so that example doesn't raise an exception. ([#1079](https://github.com/Mause/duckdb_engine/issues/1079)) ([d0688b4](https://github.com/Mause/duckdb_engine/commit/d0688b4b3e740fb357b6862ebe1ac698506f6488))

## [0.13.1](https://github.com/Mause/duckdb_engine/compare/v0.13.0...v0.13.1) (2024-07-29)


### Bug Fixes

* fix: Pass user config option via database name #1064

## [0.13.0](https://github.com/Mause/duckdb_engine/compare/v0.12.1...v0.13.0) (2024-06-02)


### Features

* first class interval support ([286abb5](https://github.com/Mause/duckdb_engine/commit/286abb585227455b4237147327cdfb5a8e90f938))


### Bug Fixes

* **deps:** update dependency duckdb to v0.10.3 ([7b5249a](https://github.com/Mause/duckdb_engine/commit/7b5249a8a22e748614ab24d91f0ed8124345591a))

## [0.12.1](https://github.com/Mause/duckdb_engine/compare/v0.12.0...v0.12.1) (2024-05-24)


### Bug Fixes

* add new types names for 0.10.3 ([8e0ca8e](https://github.com/Mause/duckdb_engine/commit/8e0ca8ee2f6d8341ea8274b465259ac4b54d312c))

## [0.12.0](https://github.com/Mause/duckdb_engine/compare/v0.12.0-rc0...v0.12.0) (2024-04-21)


### Miscellaneous Chores

* release 0.12.0 (same as rc0) ([7842f2c](https://github.com/Mause/duckdb_engine/commit/7842f2c0ad12ae9dadbbc8145ef910cb4c4d1fee))

## [0.12.0-rc0](https://github.com/Mause/duckdb_engine/compare/v0.11.5...v0.12.0-rc0) (2024-04-18)


### Bug Fixes

* allow connections to be properly closed ([0e57a64](https://github.com/Mause/duckdb_engine/commit/0e57a645f4dbdddde6ffc9a274ba104ea0070147))

### Miscellaneous Chores

* release 0.12.0-rc0 ([dc71073](https://github.com/Mause/duckdb_engine/commit/dc7107338c6b212ca6cccc7bcec398c378bd1a15))

## [0.11.5](https://github.com/Mause/duckdb_engine/compare/v0.11.4...v0.11.5) (2024-04-16)


### Miscellaneous Chores

* loosen packaging pin

## [0.11.4](https://github.com/Mause/duckdb_engine/compare/v0.11.3...v0.11.4) (2024-04-09)


### Bug Fixes

* drop python 3.7 support ([9acdd66](https://github.com/Mause/duckdb_engine/commit/9acdd660f9f50f120393128f06c12da7e89dfefd))

## [0.11.3](https://github.com/Mause/duckdb_engine/compare/v0.11.2...v0.11.3) (2024-04-07)


### Bug Fixes

* _loads_domains in SQLA2 ([4c67e26](https://github.com/Mause/duckdb_engine/commit/4c67e2616a1b5e1d86eac895ad188bafbbd1a190))
* allow parsing json in dynamic queries ([895685e](https://github.com/Mause/duckdb_engine/commit/895685e95cab1e9c5f6d3b9cd5f5f763bac9d8d1))

## [0.11.2](https://github.com/Mause/duckdb_engine/compare/v0.11.1...v0.11.2) (2024-03-01)


### Bug Fixes

* support views in has_table ([52d6a43](https://github.com/Mause/duckdb_engine/commit/52d6a43146518af85d5513c4d663ec3a8bc59bda))

## [0.11.1](https://github.com/Mause/duckdb_engine/compare/v0.11.0...v0.11.1) (2024-02-06)


### Miscellaneous Chores

* Add duckdb_engine/sqlalchemy version info to DuckDB user_agent

## [0.11.0](https://github.com/Mause/duckdb_engine/compare/v0.10.0...v0.11.0) (2024-02-04)


### Features

* comment support ([6a00ec0](https://github.com/Mause/duckdb_engine/commit/6a00ec0614e02191ee5a2d104f1fe288ea6b0d27))

## [0.10.0](https://github.com/Mause/duckdb_engine/compare/v0.9.5...v0.10.0) (2023-12-24)


### Features

* add new uhugeint type ([4e01db8](https://github.com/Mause/duckdb_engine/commit/4e01db8101121c6ee3909949ff4dcace91385e51))


### Bug Fixes

* remove packaging requirement ([5b9cafb](https://github.com/Mause/duckdb_engine/commit/5b9cafb289ad7bc391e3bac3f31fe276618deddf))

## [0.9.5](https://github.com/Mause/duckdb_engine/compare/v0.9.4...v0.9.5) (2023-12-21)


### Bug Fixes

* fix: support getting table properties using schema with db name prefix ([#848](https://github.com/Mause/duckdb_engine/pull/848))

## [0.9.4](https://github.com/Mause/duckdb_engine/compare/v0.9.3...v0.9.4) (2023-12-09)


### Bug Fixes

* fix: Support fetching multiple databases and schemas and their associated tables

## [0.9.3](https://github.com/Mause/duckdb_engine/compare/v0.9.2...v0.9.3) (2023-12-05)


### Bug Fixes

* use numeric_dollar where available ([f51ee7f](https://github.com/Mause/duckdb_engine/commit/f51ee7fb481f6e41e9d6636356edb81ee5e424cd))


### Documentation

* add directions for `alembic` support ([d549ba4](https://github.com/Mause/duckdb_engine/commit/d549ba497b1830b73b54dda4cd983ddb3114c150))
* update autoloading docs ([b782994](https://github.com/Mause/duckdb_engine/commit/b7829948114fb391918795a932564da2bbbb16db))
* update register docs ([9081ef7](https://github.com/Mause/duckdb_engine/commit/9081ef76cac0dd80b3922cc2b290724db17aa28e))
* update toc ([abcb158](https://github.com/Mause/duckdb_engine/commit/abcb158c42b734514028fbb9741c7c7dfa04f985))
* update toc ([#785](https://github.com/Mause/duckdb_engine/issues/785)) ([234a8b8](https://github.com/Mause/duckdb_engine/commit/234a8b801ffe4d236c8a790b880bc81207f37266))

## [0.9.2](https://github.com/Mause/duckdb_engine/compare/v0.9.1...v0.9.2) (2023-07-23)


### Bug Fixes

* **types:** map `uinteger` to correct type ([405769a](https://github.com/Mause/duckdb_engine/commit/405769a3b4146cb751e64d4965e94c760934b974))

## [0.9.1](https://github.com/Mause/duckdb_engine/compare/v0.9.0...v0.9.1) (2023-07-14)


### Bug Fixes

* move numpy to dev dependencies ([368c55c](https://github.com/Mause/duckdb_engine/commit/368c55cd41ceb97d4e8dc2971a100b088d2305da))

## [0.9.0](https://github.com/Mause/duckdb_engine/compare/v0.8.0...v0.9.0) (2023-06-21)


### Features

* added support for try_cast operator ([c4318ef](https://github.com/Mause/duckdb_engine/commit/c4318ef636b5a88a1cb8eccef827183884022a7b)) (see [SQLAlchemy docs](https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.try_cast) for more information)

## [0.8.0](https://github.com/Mause/duckdb_engine/compare/v0.7.3...v0.8.0) (2023-06-20)


### Features

* nested types (Struct, Map, Union) ([5c16863](https://github.com/Mause/duckdb_engine/commit/5c16863fce86a11f5bef64449f453dd8b0ef8167))
* passing config via query parameters in the url ([6907041](https://github.com/Mause/duckdb_engine/pull/675/commits/690704175dc5d61530dc3fd74b0526a638010ba6)

### Bug Fixes

* allow passing motherduck_token as a config parameter ([b944405](https://github.com/Mause/duckdb_engine/commit/b9444054260eb10c7d473dc55cb7cd7e8a0e84b6))

## [0.7.3](https://github.com/Mause/duckdb_engine/compare/v0.7.2...v0.7.3) (2023-05-19)


### Bug Fixes

* don't reflect nested types for now ([3a01f9d](https://github.com/Mause/duckdb_engine/commit/3a01f9d9d8d459c7b185b8c95f0eabe6ae21c56e))

## [0.7.2](https://github.com/Mause/duckdb_engine/compare/v0.7.1...v0.7.2) (2023-05-17)


### Bug Fixes

* add missing ischema_names entries ([20e30cf](https://github.com/Mause/duckdb_engine/commit/20e30cf4062cf3927b6dab86b0e609ca1e3d4d68))

## [0.7.1](https://github.com/Mause/duckdb_engine/compare/v0.7.0...v0.7.1) (2023-05-09)


### Bug Fixes

* reuse base dialect colspecs ([faba775](https://github.com/Mause/duckdb_engine/commit/faba77590690cd026384a1e310373661554b903a)), closes [#632](https://github.com/Mause/duckdb_engine/issues/632)


### Dependencies

* raise sqlalchemy lower bound to fix [#609](https://github.com/Mause/duckdb_engine/issues/609) ([16cc7d8](https://github.com/Mause/duckdb_engine/commit/16cc7d88f6982d572648c142a25a9e8681bb46f2))

## [0.7.0](https://github.com/Mause/duckdb_engine/compare/v0.7.0-rc1...v0.7.0) (2023-03-16)


### Miscellaneous Chores

* release 0.7.0 ([c790424](https://github.com/Mause/duckdb_engine/commit/c790424aee5f2bfcfe589ad7f27b4f2e18b4d1e2))

## [0.7.0-rc1](https://github.com/Mause/duckdb_engine/compare/v0.6.9...v0.7.0-rc1) (2023-03-07)


### Features

* support sqlalchemy 2.0 ([fe6be80](https://github.com/Mause/duckdb_engine/commit/fe6be8034aa0d3cdfce03f67cf885eafe3dd9d64))


### Miscellaneous Chores

* release 0.7.0-rc1 ([691fdf9](https://github.com/Mause/duckdb_engine/commit/691fdf918ff3caee21395ab35a1a7840a8a7f833))

## [0.6.9](https://github.com/Mause/duckdb_engine/compare/v0.6.8...v0.6.9) (2023-03-01)


### Bug Fixes

* properly support UUID type ([b138b85](https://github.com/Mause/duckdb_engine/commit/b138b8512b972c8b8ec9c229d86ae18706c8b18e)), closes [#530](https://github.com/Mause/duckdb_engine/issues/530)


### Documentation

* update README toc ([42a0192](https://github.com/Mause/duckdb_engine/commit/42a0192b8f948b610303a63f1a490c4ffe1ead95))
* update readme with link to duckdb's docs ([4fcb730](https://github.com/Mause/duckdb_engine/commit/4fcb730c9f87d2d3ebd383717fb90b329fd50708))

## [0.6.8](https://github.com/Mause/duckdb_engine/compare/v0.6.7...v0.6.8) (2023-01-08)


### Bug Fixes

* correct json type mapping ([7bf8753](https://github.com/Mause/duckdb_engine/commit/7bf8753f79aac22e2e133fd1b916950c32b0facf))

## [0.6.7](https://github.com/Mause/duckdb_engine/compare/v0.6.6...v0.6.7) (2023-01-07)


### Bug Fixes

* correct attribute reference ([d2a2577](https://github.com/Mause/duckdb_engine/commit/d2a2577cded6e6e9282efab5370b15bbe4423a40))

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

Changelog for RouterOS-api
==========================

## 0.20.0 (2025-03-07)
----------------------

- Fix decoding non utf-8 characters. Allow setting fallback encoding ([#104](https://github.com/socialwifi/RouterOS-api/pull/104)).
- Fix `TypeError: can't concat str to bytes` ([#105](https://github.com/socialwifi/RouterOS-api/pull/105)).


## 0.19.0 (2025-03-06)
----------------------

- Add support for `!empty` reply word ([#103](https://github.com/socialwifi/RouterOS-api/pull/103)).


## 0.18.1 (2024-05-28)
----------------------

- Fix tests not being run with GitHub Actions.
- Add linters.
- Fix SyntaxWarning.


## 0.18.0 (2024-04-30)
-------------------

- Drop support for end-of-life Python versions (2.7, 3.4, 3.5, 3.6, 3.7)
- Add support for new Python versions (3.9, 3.10, 3.11, 3.12)
- Add IPv6 support ([#88](https://github.com/socialwifi/RouterOS-api/pull/88))


0.17.0 (2019-09-24)
-------------------

- Add missing types of field to api_structure


0.16.0 (2019-09-24)
-------------------

- Fix bug with plain text login using string credentials ([#47](https://github.com/socialwifi/RouterOS-api/issues/47))
- Add support for new Python versions
- Drop end-of-life Python versions


0.15.0 (2018-08-23)
-------------------

- Support new login API for v6.43. ([#29](https://github.com/socialwifi/RouterOS-api/issues/29))
  
  **Backwards-incompatible**: use `plaintext_login=True` if you connect with devices with OS older than v6.43.

- Add SSL encryption. ([#30](https://github.com/socialwifi/RouterOS-api/issues/30))


0.14 (2016-04-15)
------------------

- Beginning of tracking changelog.

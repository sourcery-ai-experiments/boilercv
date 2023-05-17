# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Add `xarray` back to main requirements now that Pandas 2.0 is supported
- Specify `pandas` and `xarray` extras and remove manual pins now that extras support Python 3.11
- Publish example data and implement pipeline testing

## [0.0.1]

- Freeze requirements used for pipeline reproduction in `repro.txt` for this release
- Remove `check_cv` stage
- Make stages aware of unprocessed datasets
- Document contour finding

## [0.0.0]

- Freeze requirements used for pipeline reproduction in `repro.txt` for this release

[Unreleased]: https://github.com/blakeNaccarato/boilercv/compare/0.0.1...HEAD
[0.0.1]: https://github.com/blakeNaccarato/boilercv/compare/0.0.0...0.0.1
[0.0.0]: https://github.com/blakeNaccarato/boilercv/releases/tag/0.0.0

# ChangeLog

## Unreleased

### Added

- ManagedDecimal support

## 0.3.2 - 2024-02-28

### Fixed

- missing ESDTNFTTransfer transfer decoding

## 0.3.1 - 2024-02-26

### Added

- input decoding for internal transaction data with multi send

### Fixed

- handle case when the space for the type 'utf-8 string' is missing

## 0.3.0 - 2024-01-24

### Added

- include the constructor as an endpoint to allow for the conversion of its inputs
- custom errors classes
- allow to encode bytes, int, list and str to bytes

### Fixed:

- wrong function implementation for AbiSerializer.from_dict


## 0.2.0 - 2023-12-22

### Added

- conversion between dict and AbiSerializer
- method to decode input data from calls and queries

## 0.1.0 - 2023-12-07

Initial release

# Methodological Documentation (V3)

## 1. High-Volume Strategy
Automated extraction focused on high-density STEM rosters. The strategy leveraged regex-based parsing to normalize names and validate against university-specific subdomains.

## 2. Refinements
- **Advanced Name Normalization**: Implemented multi-pass regex to strip academic titles, professional labels, and institutional noise.
- **Subdomain Verification**: Explicitly handled @icmc.usp.br, @cos.ufrj.br, and @dcc.ufmg.br.
- **Deduplication**: Strict validation script to ensure unique records.

## 3. Ethics & LGPD
Only publicly available, institutional contacts were mapped. Ethical documentation is provided for units where data is protected.

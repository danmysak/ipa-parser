# IPA parser for Python

## Quick start
```python
from ipaparser import IPA

print([str(symbol) for symbol in IPA('[ˈpʰɹɛʔt͡sɫ̩]') if 'consonant' in symbol.features()])
```
```python
['pʰ', 'ɹ', 'ʔ', 't͡s', 'ɫ̩']
```

## Usage/reference

_Please see full documentation on [GitHub](https://github.com/danmysak/ipa-parser#readme)._

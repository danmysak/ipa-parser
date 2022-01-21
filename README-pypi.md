# IPA parser for Python

## Installation
```
pip install ipaparser
```

## Quick start
```python
from ipaparser import IPA

print([str(symbol) for symbol in IPA('[ˈpʰɹɛʔt͡sɫ̩]') if 'consonant' in symbol.features()])
```
```python
['pʰ', 'ɹ', 'ʔ', 't͡s', 'ɫ̩']
```

## Usage/reference

### `IPA`

The `IPA` class can be used to parse IPA transcriptions. It behaves as a wrapper around a list of [symbols](#IPASymbol):

```python
from ipaparser import IPA

print([
    len(IPA('[aɪ pʰiː eɪ]')),
    # 8
    
    list(IPA('[aɪ pʰiː eɪ]')),
    # [IPASymbol('a'),
    #  IPASymbol('ɪ'),
    #  IPASymbol(' '),
    #  IPASymbol('pʰ'),
    #  IPASymbol('iː'),
    #  IPASymbol(' '),
    #  IPASymbol('e'),
    #  IPASymbol('ɪ')]
    
    IPA('[aɪ pʰiː eɪ]')[0],
    # IPASymbol('a')
    
    IPA('[aɪ pʰiː eɪ]')[-1],
    # IPASymbol('ɪ')
    
    IPA('[aɪ pʰiː eɪ]')[3:5],
    # IPA('[pʰiː]')
])
```

You can control some aspects of how parsing is performed by additionally passing a [configuration](#IPAConfig):

```python
from ipaparser import IPA, IPAConfig

print([
    list(IPA('[aɪ pʰiː eɪ]', IPAConfig(combined=[('a', 'ɪ'), ('e', 'ɪ')]))),
    # [IPASymbol('a͡ɪ'),
    #  IPASymbol(' '),
    #  IPASymbol('pʰ'),
    #  IPASymbol('iː'),
    #  IPASymbol(' '),
    #  IPASymbol('e͡ɪ')]
])
```

<a name="IPA-transcription-type"></a>Objects of the `IPA` class provide basic information about their [transcription type](#TranscriptionType): 

```python
from ipaparser import IPA
from ipaparser.definitions import TranscriptionType

print([
    IPA('[aɪ pʰiː eɪ]').type,
    # <TranscriptionType.PHONETIC: 'phonetic'>
    
    IPA('/ˌaɪ.piːˈeɪ/').type == TranscriptionType.PHONEMIC,
    # True
    
    IPA('[aɪ pʰiː eɪ]').left_bracket,
    # '['
    
    IPA('[aɪ pʰiː eɪ]').right_bracket,
    # ']'
])
```

`IPA` objects can be compared with other `IPA` objects as well as with strings:

```python
from ipaparser import IPA

print([
    IPA('[aɪ pʰiː eɪ]') == IPA('[aɪ pʰiː eɪ]'),
    # True
    
    IPA('[aɪ pʰiː eɪ]') == '[aɪ pʰiː eɪ]',
    # True
    
    IPA(transcription := '[ú]') == transcription,
    # False: `IPA` performs unicode normalizations on strings
    
    IPA('[aɪ pʰiː eɪ]') == IPA('[eɪ pʰiː aɪ]'),
    # False
    
    IPA('[aɪ pʰiː eɪ]') == IPA('/aɪ pʰiː eɪ/'),
    # False
    
    IPA('[aɪ pʰiː eɪ]').as_string(),
    # '[aɪ pʰiː eɪ]'
    
    str(IPA('[aɪ pʰiː eɪ]')),
    # '[aɪ pʰiː eɪ]'
])
```

You can concatenate multiple `IPA` objects as well as append or prepend symbols to them:

```python
from ipaparser import IPA, IPASymbol

print([
    IPA('[aɪ pʰiː]') + IPASymbol(' ') + IPA('[eɪ]'),
    # IPA('[aɪ pʰiː eɪ]')
    
    IPA('[aɪ]') * 3,
    # IPA('[aɪaɪaɪ]')
])
```

### `IPASymbol`

`IPASymbol` represents an individual unit of IPA transcriptions: either a sound (like `a`, `t͡s`, or `ᶢǁʱ`), a break (like `.` or a space), a suprasegmental letter (stress mark, tone number, etc.), or an unknown grapheme.

```python
from ipaparser import IPA, IPASymbol

print([
    IPA('[aɪ pʰiː]')[0].is_sound(),
    # True
    
    IPA('[aɪ pʰiː]')[2].is_sound(),
    # False
    
    IPA('[aɪ pʰiː]')[2].is_break(),
    # True
    
    IPASymbol('˦').is_suprasegmental(),
    # True
    
    IPASymbol('˦').is_known(),
    # True
    
    IPASymbol('*').is_known(),
    # False
])
```

Just as with the `IPA` constructor, you can additionally pass to `IPASymbol` a [configuration](#IPAConfig):

```python
from ipaparser import IPAConfig, IPASymbol

print([
    IPASymbol('g:').is_known(),
    # False
    
    IPASymbol('g:', IPAConfig(substitutions=True)),
    # IPASymbol('ɡː')
    
    IPASymbol('g:', IPAConfig(substitutions=True)).is_known(),
    # True
])
```

Symbols can be queried for their [features](#Features):

```python
from ipaparser import IPASymbol
from ipaparser.features import Aspiration, Backness, Height, Manner, SoundType

print([
    IPASymbol('pʰ').features(),
    # frozenset({<Aspiration.ASPIRATED: 'aspirated'>,
    #            <Place.BILABIAL: 'bilabial'>,
    #            <SoundType.CONSONANT: 'consonant'>,
    #            <PlaceCategory.LABIAL: 'labial'>,
    #            <SoundSubtype.SIMPLE_CONSONANT: 'simple consonant'>,
    #            <SymbolType.SOUND: 'sound'>,
    #            <Manner.STOP: 'stop'>})
    
    IPASymbol('a').features({Backness, Height}),
    # frozenset({<Backness.FRONT: 'front'>,
    #            <Height.OPEN: 'open'>})
    
    IPASymbol('s').features(Manner),
    # frozenset({<Manner.FRICATIVE: 'fricative'>,
    #            <Manner.SIBILANT: 'sibilant'>})
    
    IPASymbol('b').features('voicing'),  # shortcut to `ipaparser.features.Voicing`
    # frozenset({<Voicing.VOICED: 'voiced'>})
    
    IPASymbol(' ').features(),
    # frozenset({<SymbolType.BREAK: 'break'>,
    #            <BreakType.SPACE: 'space'>})
    
    IPASymbol('*').features(),
    # None
    
    IPASymbol('pʰ').has_feature(Aspiration.ASPIRATED),
    # True
    
    IPASymbol('a').has_feature('vowel'),  # shortcut to `ipaparser.features.SoundType.VOWEL`
    # True
    
    IPASymbol('b').has_feature(SoundType.VOWEL),
    # False
    
    IPASymbol('*').has_feature(SoundType.VOWEL),
    # False
])
```

Some sounds may be requested for alternative interpretations:
1) Nonsyllabic front/back close vowels (`i̯`, `y̑`, `ɯ̯`, `u̯`) can be reinterpreted as palatal/velar approximants (`j`, `ɥ`, `ɰ`, `w`).
2) “Ambiguous” as to the exact place of articulation consonants such as `t`, `n`, `ǁ`, etc., which are treated as alveolar by default, can be reinterpreted as dental or as postalveolar.
3) Ad-hoc grapheme combinations used in the IPA (e.g., `ä` for the open central unrounded vowel) can be alternatively treated literally (so that `ä` becomes a centralized open front unrounded vowel).

```python
from ipaparser import IPASymbol
from ipaparser.features import Place, SoundType

print([
    IPASymbol('i̯').features(SoundType),
    # frozenset({<SoundType.VOWEL: 'vowel'>})
    
    IPASymbol('i̯').features(role=SoundType.CONSONANT),
    # frozenset({<Manner.APPROXIMANT: 'approximant'>,
    #            <SoundType.CONSONANT: 'consonant'>,
    #            <PlaceCategory.DORSAL: 'dorsal'>,
    #            <Place.PALATAL: 'palatal'>,
    #            <SoundSubtype.SIMPLE_CONSONANT: 'simple consonant'>,
    #            <SymbolType.SOUND: 'sound'>,
    #            <Voicing.VOICED: 'voiced'>})
    
    IPASymbol('i̯').features(role='consonant') == IPASymbol('j').features(),
    # True
    
    IPASymbol('t').features(Place),
    # frozenset({<Place.ALVEOLAR: 'alveolar'>})
    
    IPASymbol('t').features(Place, role=Place.POSTALVEOLAR),
    # frozenset({<Place.POSTALVEOLAR: 'postalveolar'>})
    
    IPASymbol('t').features(Place, role=Place.DENTAL),
    # frozenset({<Place.DENTAL: 'dental'>})
    
    IPASymbol('t').features(Place, role=Place.BILABIAL),
    # None
    
    IPASymbol('ɹ̠̊˔').features(),
    # frozenset({<SoundType.CONSONANT: 'consonant'>,
    #            <PlaceCategory.CORONAL: 'coronal'>,
    #            <Manner.FRICATIVE: 'fricative'>,
    #            <Place.POSTALVEOLAR: 'postalveolar'>,
    #            <SoundSubtype.SIMPLE_CONSONANT: 'simple consonant'>,
    #            <SymbolType.SOUND: 'sound'>})
    
    IPASymbol('ɹ̠̊˔').features(role=Place.ALVEOLAR),
    # frozenset({<Place.ALVEOLAR: 'alveolar'>,
    #            <Manner.APPROXIMANT: 'approximant'>,
    #            <SoundType.CONSONANT: 'consonant'>,
    #            <PlaceCategory.CORONAL: 'coronal'>,
    #            <Articulation.RAISED: 'raised'>,
    #            <Articulation.RETRACTED: 'retracted'>,
    #            <SoundSubtype.SIMPLE_CONSONANT: 'simple consonant'>,
    #            <SymbolType.SOUND: 'sound'>})
])
```

Symbols preserve information about their constituents:

```python
from ipaparser import IPASymbol
from ipaparser.features import Manner

print([
    IPASymbol('ts').features(Manner),
    # frozenset({<Manner.AFFRICATE: 'affricate'>,
    #            <Manner.SIBILANT: 'sibilant'>})
    
    IPASymbol('ts').components,
    # (IPASymbol('t'), IPASymbol('s'))
    
    IPASymbol('ts').left,
    # IPASymbol('t')
    
    IPASymbol('ts').left.features(Manner),
    # frozenset({<Manner.STOP: 'stop'>})
    
    IPASymbol('ts').right.features(Manner),
    # frozenset({<Manner.FRICATIVE: 'fricative'>,
    #            <Manner.SIBILANT: 'sibilant'>})
    
    IPASymbol('t͡s').components == IPASymbol('ts').components,
    # True
    
    IPASymbol('t').components,
    # None
    
    IPASymbol('d͢').is_known(),
    # False
    
    IPASymbol('d͢').components,
    # (IPASymbol('d'),)
    
    IPASymbol('d͢').components[0].is_known(),
    # True
])
```

`IPASymbol` objects can be compared with other symbols as well as with strings:

```python
from ipaparser import IPASymbol

print([
    IPASymbol('ts') == IPASymbol('ts'),
    # True
    
    IPASymbol('ts') == 'ts',
    # True
    
    IPASymbol(symbol := 'ú') == symbol,
    # False: `IPASymbol` performs unicode normalizations on strings
    
    IPASymbol('ts').features() == IPASymbol('t͡s').features(),
    # True
    
    IPASymbol('ts') == IPASymbol('t͡s'),
    # False: underlying strings are compared, not features
    
    IPASymbol('ts').as_string(),
    # 'ts'
    
    str(IPASymbol('ts')),
    # 'ts'
])
```

### `IPAConfig`

`IPAConfig` can be used to control some aspects of how transcriptions and individual symbols are parsed. The following parameters are available for configuration:

| Parameter       | Type(s)                                        | Default                            | Description                                                                                                                                                                                                                                                   |
|-----------------|------------------------------------------------|------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `substitutions` | `bool`                                         | `False`                            | Whether to perform normalizing substitutions that allow to properly handle commonly observed simplifications in IPA notation such as the Latin letter `g` being used instead of the IPA’s dedicated character `ɡ` or a colon in place of the length mark `ː`. |
| `brackets`      | [`BracketStrategy`](#BracketStrategy)<br>`str` | `BracketStrategy.KEEP`<br>`'keep'` | What to do with content in brackets denoting optional pronunciation, such as in `[bə(j)ɪz⁽ʲ⁾ˈlʲivɨj]`:<ul><li>`keep` (and treat brackets as invalid IPA characters);</li><li>`expand`: `[bəjɪzʲˈlʲivɨj]`;</li><li>`strip`: `[bəɪzˈlʲivɨj]`.</li></ul>         |
| `combined`      | `Iterable[tuple[str, ...]]`                    | `()`                               | Sound sequences to be treated as though they were connected by a tie, e.g., `[('t', 's'), ('d̠', 'ɹ̠˔'), ('a', 'ɪ'), ('u̯', 'e', 'i̯')]`.<br>Note that, say, `('a', 'ɪ')` will not match `'aɪ̯'`, and likewise `('a', 'ɪ̯')` will not match `'aɪ'`.           |

```python
from ipaparser import IPA, IPAConfig, IPASymbol
from ipaparser.definitions import BracketStrategy

print([
    IPA('/ɹɪˈdʒɔɪndʒə(ɹ)/', IPAConfig(brackets=BracketStrategy.STRIP, combined=[('d', 'ʒ'), ('ɔ', 'ɪ')])),
    # IPA('/ɹɪˈd͡ʒɔ͡ɪnd͡ʒə/')
    
    IPASymbol('o(:)', IPAConfig(substitutions=True, brackets='expand'))
    # IPASymbol('oː')
])
```

### `load`

Call this function to eagerly load and preprocess supporting data so that the first parse is a little faster. Compare:

```python
from timeit import timeit

from ipaparser import IPA

print([
    timeit(lambda: IPA('[aɪ pʰiː eɪ]'), number=1),
    # 0.007

    timeit(lambda: IPA('[ˈpʰɹɛʔt͡sɫ̩]'), number=1),
    # 0.0004
])
```

```python
from timeit import timeit

from ipaparser import IPA, load

load()

print([
    timeit(lambda: IPA('[aɪ pʰiː eɪ]'), number=1),
    # 0.0002

    timeit(lambda: IPA('[ˈpʰɹɛʔt͡sɫ̩]'), number=1),
    # 0.0004
])
```


### Definitions

#### `BracketStrategy`

For usage, see [IPAConfig](#IPAConfig).

| Value                    | String representation |
|--------------------------|-----------------------|
| `BracketStrategy.KEEP`   | `keep`                |
| `BracketStrategy.EXPAND` | `expand`              |
| `BracketStrategy.STRIP`  | `strip`               |

#### `TranscriptionType`

For usage, see [IPA transcription type](#IPA-transcription-type).

| Value                        | String representation | Brackets |
|------------------------------|-----------------------|----------|
| `TranscriptionType.PHONETIC` | `phonetic`            | `[...]`  |
| `TranscriptionType.PHONEMIC` | `phonemic`            | `/.../`  |
| `TranscriptionType.LITERAL`  | `literal`             | `⟨...⟩`  |


### Exceptions

```python
from ipaparser import IPA, IPAConfig, IPASymbol
from ipaparser.exceptions import (
    BracketStrategyError,
    CombinedLengthError,
    CombinedSoundError,
    EnclosingError,
    FeatureError,
    FeatureKindError,
    IncompatibleTypesError,
)

try:
    config = IPAConfig(brackets='custom')
except BracketStrategyError as e:
    print(str(e))  # 'custom' is not a valid strategy; use one of the following: 'keep'/'expand'/'strip'
    print(e.value)  # 'custom'

try:
    config = IPAConfig(combined=[('t', 's'), ('e',)])
except CombinedLengthError as e:
    print(str(e))  # A sound sequence to be combined must contain at least 2 elements (got 1: 'e')
    print(e.sequence)  # ('e',)

try:
    config = IPAConfig(combined=[('t', 's'), ('i', '̯ɐ')])
except CombinedSoundError as e:
    print(str(e))  # A sound to be combined must start with a non-combining character (got ' ̯ɐ')
    print(e.sound)  # '̯ɐ'

try:
    config = IPAConfig(combined=[('t', 's'), ('i', '')])
except CombinedSoundError as e:
    print(str(e))  # A sound to be combined cannot be empty
    print(e.sound)  # ''

try:
    ipa = IPA('aɪ pʰiː eɪ')
except EnclosingError as e:
    print(str(e))  # 'aɪ pʰiː eɪ' is not properly delimited (like [so] or /so/)
    print(e.transcription)  # 'aɪ pʰiː eɪ'

try:
    is_vowel = IPASymbol('a').has_feature('vocalic')
except FeatureError as e:
    print(str(e))  # Invalid feature: 'vocalic'
    print(e.value)  # 'vocalic'

try:
    features = IPASymbol('a').features('sonority')
except FeatureKindError as e:
    print(str(e))  # Invalid feature kind: 'sonority'
    print(e.value)  # 'sonority'

try:
    concatenated = IPA('[a]') + IPA('/b/')
except IncompatibleTypesError as e:
    print(str(e))  # '[a]' and '/b/' have incompatible types and cannot be concatenated
    print(e.left)  # '[a]'
    print(e.right)  # '/b/'
```

### Features

_Please see [this section on GitHub](https://github.com/danmysak/ipa-parser#features) as there is [an issue](https://github.com/pypa/warehouse/issues/5878) with how PyPI displays it._

### Feature typing and helper methods

You can iterate through the supported features using the tuple `FEATURE_KINDS`. Feature kinds (such as `Height`, `Manner`, or `Voicing`) are all string-based enums subclassed off of the base class `Feature`. Feature kinds themselves have the type `Type[Feature]`, aliased `FeatureKind`. The `.kind_values()` method can be called to retrieve supported string representations of the feature kind. 

```python
from ipaparser.features import Feature, FEATURE_KINDS, FeatureKind

kind: FeatureKind
for kind in FEATURE_KINDS:
    print(kind)
    # <enum 'Airflow'>, <enum 'Articulation'>, ..., <enum 'ToneType'>, <enum 'Voicing'>
    print(kind.kind_values())
    # ('Airflow', 'airflow'), ('Articulation', 'articulation'), ..., ('ToneType', 'tone type'), ('Voicing', 'voicing')
    
    feature: Feature
    for feature in kind:
        print(feature)
        # Airflow.EGRESSIVE_AIRFLOW, Airflow.INGRESSIVE_AIRFLOW, Articulation.APICAL, ..., Voicing.DEVOICED
        print(feature.value)
        # 'egressive airflow', 'ingressive airflow', 'apical', ..., 'devoiced'
```

`FeatureSet` (which can be imported from `ipaparser.features`) is an alias for `frozenset[Feature]`. The return type of `IPASymbol.features()` is hence `Optional[FeatureSet]`.

Finally, the `.derived()` and `.extend()` methods of individual features may be called to obtain basic hierarchical relationships between features:

```python
from ipaparser.features import Place, ToneLetter

print(Place.ALVEOLAR.derived())  # get the most specific derived feature
# PlaceCategory.CORONAL

print(ToneLetter.HIGH_TONE_LETTER.extend())  # all the derived features, including the caller
# frozenset({<ToneLetter.HIGH_TONE_LETTER: 'high tone letter'>,
#            <ToneType.TONE_LETTER: 'tone letter'>,
#            <SuprasegmentalType.TONE: 'tone'>,
#            <SymbolType.SUPRASEGMENTAL: 'suprasegmental'>})
```

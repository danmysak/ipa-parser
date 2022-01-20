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

print(
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
)
```

You can control some aspects of how parsing is performed by additionally passing a [configuration](#IPAConfig):

```python
from ipaparser import IPA, IPAConfig

print(
    list(IPA('[aɪ pʰiː eɪ]', IPAConfig(combined=[('a', 'ɪ'), ('e', 'ɪ')]))),
    # [IPASymbol('a͡ɪ'),
    #  IPASymbol(' '),
    #  IPASymbol('pʰ'),
    #  IPASymbol('iː'),
    #  IPASymbol(' '),
    #  IPASymbol('e͡ɪ')]
)
```

<a name="IPA-transcription-type"></a>Objects of the `IPA` class provide basic information about their [transcription type](#TranscriptionType): 

```python
from ipaparser import IPA
from ipaparser.definitions import TranscriptionType

print(
    IPA('[aɪ pʰiː eɪ]').type,
    # <TranscriptionType.PHONETIC: 'phonetic'>
    
    IPA('/ˌaɪ.piːˈeɪ/').type == TranscriptionType.PHONEMIC,
    # True
    
    IPA('[aɪ pʰiː eɪ]').left_bracket,
    # '['
    
    IPA('[aɪ pʰiː eɪ]').right_bracket,
    # ']'
)
```

`IPA` objects can be compared with other `IPA` objects as well as with strings:

```python
from ipaparser import IPA

print(
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
)
```

You can concatenate multiple `IPA` objects as well as append or prepend symbols to them:

```python
from ipaparser import IPA, IPASymbol

print(
    IPA('[aɪ pʰiː]') + IPASymbol(' ') + IPA('[eɪ]'),
    # IPA('[aɪ pʰiː eɪ]')
    
    IPA('[aɪ]') * 3,
    # IPA('[aɪaɪaɪ]')
)
```

### `IPASymbol`

`IPASymbol` represents an individual unit of IPA transcriptions: either a sound (like `a`, `t͡s`, or `ᶢǁʱ`), a break (like `.` or a space), a suprasegmental letter (stress mark, tone number, etc.), or an unknown grapheme.

```python
from ipaparser import IPA, IPASymbol

print(
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
)
```

Just as with the `IPA` constructor, you can additionally pass to `IPASymbol` a [configuration](#IPAConfig):

```python
from ipaparser import IPAConfig, IPASymbol

print(
    IPASymbol('g:').is_known(),
    # False
    
    IPASymbol('g:', IPAConfig(substitutions=True)),
    # IPASymbol('ɡː')
    
    IPASymbol('g:', IPAConfig(substitutions=True)).is_known(),
    # True
)
```

Symbols can be queried for their [features](#Features):

```python
from ipaparser import IPASymbol
from ipaparser.features import Aspiration, Backness, Height, Manner, SoundType

print(
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
)
```

Some sounds may be requested for alternative interpretations:
1) Nonsyllabic front/back close vowels (`i̯`, `y̑`, `ɯ̯`, `u̯`) can be reinterpreted as palatal/velar approximants (`j`, `ɥ`, `ɰ`, `w`).
2) “Ambiguous” as to the exact place of articulation consonants such as `t`, `n`, `ǁ`, etc., which are treated as alveolar by default, can be reinterpreted as dental or as postalveolar.
3) Ad-hoc grapheme combinations used in the IPA (e.g., `ä` for the open central unrounded vowel) can be alternatively treated literally (so that `ä` becomes a centralized open front unrounded vowel).

```python
from ipaparser import IPASymbol
from ipaparser.features import Place, SoundType

print(
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
)
```

Symbols preserve information about their constituents:

```python
from ipaparser import IPASymbol
from ipaparser.features import Manner

print(
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
)
```

`IPASymbol` can be compared with other `IPASymbol` objects as well as with strings:

```python
from ipaparser import IPASymbol

print(
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
)
```

### `IPAConfig`

`IPAConfig` can be used to control some aspects of how transcriptions and individual symbols are parsed. The following parameters are available for configuration:

| Parameter       | Type(s)                                        | Default                            | Description                                                                                                                                                                                                                                           |
|-----------------|------------------------------------------------|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `substitutions` | `bool`                                         | `False`                            | Whether to perform normalizing substitutions that allow to properly handle commonly observed simplifications such as Latin `g` being used instead of the IPA’s dedicated character `ɡ` or a colon being used instead of the length mark `ː`.          |
| `brackets`      | [`BracketStrategy`](#BracketStrategy)<br>`str` | `BracketStrategy.KEEP`<br>`'keep'` | What to do with content in brackets denoting optional pronunciation, such as in `[bə(j)ɪz⁽ʲ⁾ˈlʲivɨj]`:<ul><li>`keep` (and treat brackets as invalid IPA characters);</li><li>`expand`: `[bəjɪzʲˈlʲivɨj]`;</li><li>`strip`: `[bəɪzˈlʲivɨj]`.</li></ul> |
| `combined`      | `Iterable[tuple[str, ...]]`                    | `()`                               | Sound sequences to be treated as though they were connected by a tie, e.g., `[('t', 's'), ('d̠', 'ɹ̠˔'), ('a', 'ɪ'), ('u̯', 'e', 'i̯')]`.<br>Note that, say, `('a', 'ɪ')` will not match `'aɪ̯'`, and likewise `('a', 'ɪ̯')` will not match `'aɪ'`.   |

```python
from ipaparser import IPA, IPAConfig, IPASymbol
from ipaparser.definitions import BracketStrategy

print(
    IPA('/ɹɪˈdʒɔɪndʒə(ɹ)/', IPAConfig(brackets=BracketStrategy.STRIP, combined=[('d', 'ʒ'), ('ɔ', 'ɪ')])),
    # IPA('/ɹɪˈd͡ʒɔ͡ɪnd͡ʒə/')
    
    IPASymbol('o(:)', IPAConfig(substitutions=True, brackets='expand'))
    # IPASymbol('oː')
)
```

### `load`

Call this function to eagerly load and preprocess supporting data so that the first parse is a little faster. Compare:

```python
from timeit import timeit

from ipaparser import IPA

print(
    timeit(lambda: IPA('[aɪ pʰiː eɪ]'), number=1),
    # 0.007

    timeit(lambda: IPA('[ˈpʰɹɛʔt͡sɫ̩]'), number=1),
    # 0.0004
)
```

```python
from timeit import timeit

from ipaparser import IPA, load

load()

print(
    timeit(lambda: IPA('[aɪ pʰiː eɪ]'), number=1),
    # 0.0002

    timeit(lambda: IPA('[ˈpʰɹɛʔt͡sɫ̩]'), number=1),
    # 0.0004
)
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

#### `Airflow`/`'airflow'` [[1]](https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics)
| Value                        | String representation | Examples |
| ---------------------------- | --------------------- | -------- |
| `Airflow.EGRESSIVE_AIRFLOW`  | `egressive airflow`   | `↑`      |
| `Airflow.INGRESSIVE_AIRFLOW` | `ingressive airflow`  | `↓`      |

#### `Articulation`/`'articulation'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation)
| Value                          | String representation | Examples             |
| ------------------------------ | --------------------- | -------------------- |
| `Articulation.APICAL`          | `apical`              | `s̺`, `z̺`, `ɾ̺`     |
| `Articulation.LAMINAL`         | `laminal`             | `s̻`, `z̻`, `n̻`     |
| `Articulation.ADVANCED`        | `advanced`            | `ɯ̟ᵝ`, `o̞˖`, `ʎ̟`   |
| `Articulation.RETRACTED`       | `retracted`           | `a̠`, `ð̩˕˗ˠˀ`, `i̠` |
| `Articulation.CENTRALIZED`     | `centralized`         | `æ̈`, `ɑ̈ː`, `ö`    |
| `Articulation.MID_CENTRALIZED` | `mid-centralized`     | `e̽`, `ɯ̥̽`, `ɤ̽`    |
| `Articulation.RAISED`          | `raised`              | `ɛ̝`, `ʎ̥˔`, `e̝ˀ`   |
| `Articulation.LOWERED`         | `lowered`             | `ʏ̞`, `ò˕`, `ɛ̞̃`   |

#### `Aspiration`/`'aspiration'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation), [[2]](https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics)
| Value                     | String representation | Examples             |
| ------------------------- | --------------------- | -------------------- |
| `Aspiration.ASPIRATED`    | `aspirated`           | `tʰ`, `kʰː`, `ǀʰ`    |
| `Aspiration.UNASPIRATED`  | `unaspirated`         | `ʔ˭`, `p˭`           |
| `Aspiration.PREASPIRATED` | `preaspirated`        | `ʰt͡s`, `ʰkʰʲ`, `ʰp` |

#### `Backness`/`'backness'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Vowels)
| Value                 | String representation | Examples          |
| --------------------- | --------------------- | ----------------- |
| `Backness.FRONT`      | `front`               | `a`, `ɛ̀ː`, `ǽ`  |
| `Backness.NEAR_FRONT` | `near-front`          | `ɪ`, `ʏ˞`, `ɪˑ`   |
| `Backness.CENTRAL`    | `central`             | `ə`, `ʉ́`, `ɘ̯`   |
| `Backness.NEAR_BACK`  | `near-back`           | `ʊ`, `ʊ́`, `ʊ̂`   |
| `Backness.BACK`       | `back`                | `o`, `ü`, `ɯ̟̃ᵝ` |

#### `BacknessCategory`/`'backness category'`
| Value                            | String representation | Examples          |
| -------------------------------- | --------------------- | ----------------- |
| `BacknessCategory.ABOUT_FRONT`   | `about front`         | `a`, `ɪ̙́`, `ʏ˞`  |
| `BacknessCategory.ABOUT_CENTRAL` | `about central`       | `ə`, `ʉ́`, `ɘ̯`   |
| `BacknessCategory.ABOUT_BACK`    | `about back`          | `o`, `ü`, `ɯ̟̃ᵝ` |

#### `BreakType`/`'break type'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals)
| Value                      | String representation | Examples |
| -------------------------- | --------------------- | -------- |
| `BreakType.SPACE`          | `space`               | ` `      |
| `BreakType.HYPHEN`         | `hyphen`              | `-`      |
| `BreakType.LINKING`        | `linking`             | `‿`      |
| `BreakType.SYLLABLE_BREAK` | `syllable break`      | `.`      |
| `BreakType.MINOR_BREAK`    | `minor break`         | `|`      |
| `BreakType.MAJOR_BREAK`    | `major break`         | `‖`      |
| `BreakType.EQUIVALENCE`    | `equivalence`         | `~`, `⁓` |
| `BreakType.ELLIPSIS`       | `ellipsis`            | `…`      |

#### `Height`/`'height'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Vowels)
| Value               | String representation | Examples           |
| ------------------- | --------------------- | ------------------ |
| `Height.CLOSE`      | `close`               | `i`, `ṳ̌ː`, `ʉ̀`  |
| `Height.NEAR_CLOSE` | `near-close`          | `ɪ`, `ʏ˞`, `ʊ̯ˑ`   |
| `Height.CLOSE_MID`  | `close-mid`           | `e`, `ɤː`, `o̟`    |
| `Height.MID`        | `mid`                 | `ə`, `ɚː`, `ɤ̞`    |
| `Height.OPEN_MID`   | `open-mid`            | `ɛ`, `ɔ̃ː`, `ɜ˞`   |
| `Height.NEAR_OPEN`  | `near-open`           | `ɐ`, `ǽ`, `ɐ̆`    |
| `Height.OPEN`       | `open`                | `a`, `ɒ̯̽ˀ`, `ɑ̃ː` |

#### `HeightCategory`/`'height category'`
| Value                        | String representation | Examples         |
| ---------------------------- | --------------------- | ---------------- |
| `HeightCategory.ABOUT_CLOSE` | `about close`         | `i`, `ʏ˞`, `ʊ̯ˑ` |
| `HeightCategory.ABOUT_MID`   | `about mid`           | `ə`, `ɘ̯`, `ø̃`  |
| `HeightCategory.ABOUT_OPEN`  | `about open`          | `a`, `ɑ̆`, `æːˀ` |

#### `Intonation`/`'intonation'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals)
| Value                    | String representation | Examples |
| ------------------------ | --------------------- | -------- |
| `Intonation.GLOBAL_RISE` | `global rise`         | `↗`      |
| `Intonation.GLOBAL_FALL` | `global fall`         | `↘`      |

#### `Length`/`'length'` [[1]](https://en.wikipedia.org/wiki/Length_(phonetics))
| Value                | String representation | Examples             |
| -------------------- | --------------------- | -------------------- |
| `Length.EXTRA_SHORT` | `extra-short`         | `n̆`, `ø̆`, `ŏ`     |
| `Length.HALF_LONG`   | `half-long`           | `äˑ`, `e̞ˑ`, `øˑ`   |
| `Length.LONG`        | `long`                | `aː`, `l̺ː`, `ɞː`    |
| `Length.EXTRA_LONG`  | `extra-long`          | `øːˑ`, `ɛːː`, `ɨˤːː` |

#### `Manner`/`'manner'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Consonants)
| Value                | String representation | Examples              |
| -------------------- | --------------------- | --------------------- |
| `Manner.AFFRICATE`   | `affricate`           | `t͡s`, `d͡zː`, `q͡χʷ` |
| `Manner.APPROXIMANT` | `approximant`         | `l`, `w̥ʰ`, `ɻ̊`      |
| `Manner.FRICATIVE`   | `fricative`           | `s`, `ʂ͜ʲ`, `xʼ`      |
| `Manner.LATERAL`     | `lateral`             | `l`, `t͡ɬʼ`, `ŋ͜ǁ`    |
| `Manner.NASAL`       | `nasal`               | `n`, `mʷ`, `ɳ̩`       |
| `Manner.SIBILANT`    | `sibilant`            | `s`, `ʑː`, `t͡ʃʲ`     |
| `Manner.STOP`        | `stop`                | `k`, `tʲʰː`, `qˤ`     |
| `Manner.TAP_FLAP`    | `tap/flap`            | `ɾ`, `ɽ̃`, `ɺ`        |
| `Manner.TRILL`       | `trill`               | `r`, `ʀ̟`, `ʙ`        |
| `Manner.CLICK`       | `click`               | `ǃ`, `ᵑǀʱ`, `ǁ`       |
| `Manner.EJECTIVE`    | `ejective`            | `tʼ`, `ɬˤʼ`, `kʼʷ`    |
| `Manner.IMPLOSIVE`   | `implosive`           | `ɓ`, `ʄ`, `ɗʲ`        |

#### `Phonation`/`'phonation'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation), [[2]](https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics)
| Value                | String representation | Examples            |
| -------------------- | --------------------- | ------------------- |
| `Phonation.BREATHY`  | `breathy`             | `bʱ`, `ṳ̌`, `ᵑǀʱ`  |
| `Phonation.CREAKY`   | `creaky`              | `æ̰ˀ`, `ɑ̰́ː`, `j̰` |
| `Phonation.WHISPERY` | `whispery`            | `ạ`, `ạ̀`, `x̣`   |

#### `Place`/`'place'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Consonants)
| Value                         | String representation   | Examples           |
| ----------------------------- | ----------------------- | ------------------ |
| `Place.BILABIAL`              | `bilabial`              | `m`, `b̥ˀ`, `p͡f`  |
| `Place.LABIODENTAL`           | `labiodental`           | `f`, `ᶬv`, `ʋ̥`    |
| `Place.LINGUOLABIAL`          | `linguolabial`          | `n̼`, `θ̼`         |
| `Place.DENTAL`                | `dental`                | `t̪`, `ðˠ`, `ɡ̊ǀ`  |
| `Place.ALVEOLAR`              | `alveolar`              | `n`, `t͜ɬ`, `lʱ`   |
| `Place.POSTALVEOLAR`          | `postalveolar`          | `ʃ`, `d͡ʒʲ`, `t̠̚` |
| `Place.RETROFLEX`             | `retroflex`             | `ʂ`, `ʈⁿ`, `ɽʷ`    |
| `Place.PALATAL`               | `palatal`               | `j`, `ɟʱ`, `kǂʰ`   |
| `Place.VELAR`                 | `velar`                 | `k`, `ɡ̞`, `xʼ`    |
| `Place.UVULAR`                | `uvular`                | `ʁ`, `q͡χʷ`, `ʀ̥`  |
| `Place.PHARYNGEAL_EPIGLOTTAL` | `pharyngeal/epiglottal` | `ħ`, `ʕː`, `ħʷ`    |
| `Place.GLOTTAL`               | `glottal`               | `ʔ`, `ɦʲ`, `hː`    |

#### `PlaceCategory`/`'place category'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Consonants)
| Value                     | String representation | Examples           |
| ------------------------- | --------------------- | ------------------ |
| `PlaceCategory.LABIAL`    | `labial`              | `m`, `b̥ˀ`, `ᶬv`   |
| `PlaceCategory.CORONAL`   | `coronal`             | `n`, `t͡ʃʲ`, `d̥̚` |
| `PlaceCategory.DORSAL`    | `dorsal`              | `k`, `q͡χʷ`, `ʎ̥˔` |
| `PlaceCategory.LARYNGEAL` | `laryngeal`           | `ʔ`, `h̃`, `ɦʲ`    |

#### `Release`/`'release'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation)
| Value                                                   | String representation                           | Examples          |
| ------------------------------------------------------- | ----------------------------------------------- | ----------------- |
| `Release.NO_AUDIBLE_RELEASE`                            | `no audible release`                            | `t̚`, `ʔ̚`, `d̪̚` |
| `Release.NASAL_RELEASE`                                 | `nasal release`                                 | `tⁿ`, `t̪ⁿ`, `ʈⁿ` |
| `Release.LATERAL_RELEASE`                               | `lateral release`                               | `tˡ`, `bˡ`, `ᵐbˡ` |
| `Release.VOICELESS_DENTAL_FRICATIVE_RELEASE`            | `voiceless dental fricative release`            | `tᶿ`              |
| `Release.VOICELESS_ALVEOLAR_SIBILANT_FRICATIVE_RELEASE` | `voiceless alveolar sibilant fricative release` | `tˢ`, `kˢ`, `tˢʰ` |
| `Release.VOICELESS_VELAR_FRICATIVE_RELEASE`             | `voiceless velar fricative release`             | `kˣ`              |

#### `Roundedness`/`'roundedness'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Vowels)
| Value                 | String representation | Examples          |
| --------------------- | --------------------- | ----------------- |
| `Roundedness.ROUNDED` | `rounded`             | `o`, `ṳ̌ː`, `ʉ̀` |

#### `RoundednessModifier`/`'roundedness modifier'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation), [[2]](https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics)
| Value                                  | String representation | Examples            |
| -------------------------------------- | --------------------- | ------------------- |
| `RoundednessModifier.MORE_ROUNDED`     | `more rounded`        | `ʌ̹`, `ə̹`, `ɔ̹`    |
| `RoundednessModifier.LESS_ROUNDED`     | `less rounded`        | `w̜`, `ɒ̜˔ː`, `ɔ̜ˑ` |
| `RoundednessModifier.COMPRESSED`       | `compressed`          | `ɯ̟ᵝ`, `ɨ̃ᵝ`, `ɰᵝ`  |
| `RoundednessModifier.LABIAL_SPREADING` | `labial spreading`    | `u͍`, `u͍ː`, `w͍`   |

#### `SecondaryModifier`/`'secondary modifier'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation), [[2]](https://en.wikipedia.org/wiki/Prenasalized_consonant), [[3]](https://en.wikipedia.org/wiki/Pre-stopped_consonant), [[4]](https://linguistics.ucla.edu/people/keating/Keating_JIPA_diacritics_accepted_complete_Feb2019.pdf), [[5]](https://en.wikipedia.org/wiki/Glottalized_click#Preglottalized_nasal_clicks)
| Value                                        | String representation      | Examples            |
| -------------------------------------------- | -------------------------- | ------------------- |
| `SecondaryModifier.ADVANCED_TONGUE_ROOT`     | `advanced tongue root`     | `ɨ̘`, `ɤ̘`, `í̘ː`  |
| `SecondaryModifier.RETRACTED_TONGUE_ROOT`    | `retracted tongue root`    | `ɪ̙̞`, `ɒ̙̀`, `ʊ̙́` |
| `SecondaryModifier.R_COLORED`                | `r-colored`                | `ɚ`, `ɝˑ`, `ɑ˞`     |
| `SecondaryModifier.NASALIZED`                | `nasalized`                | `ĩ`, `õ̤`, `ɯ̟̃ᵝ` |
| `SecondaryModifier.PRENASALIZED`             | `prenasalized`             | `ⁿdˠ`, `n͡t`, `ᶬv`  |
| `SecondaryModifier.VOICELESSLY_PRENASALIZED` | `voicelessly prenasalized` | `m̥͡bʷ`             |
| `SecondaryModifier.PRESTOPPED`               | `prestopped`               | `ᵈn`, `ᵇm`, `ᵈl`    |
| `SecondaryModifier.PREGLOTTALIZED`           | `preglottalized`           | `ˀt`, `ˀd`          |

#### `SecondaryPlace`/`'secondary place'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation)
| Value                           | String representation | Examples           |
| ------------------------------- | --------------------- | ------------------ |
| `SecondaryPlace.LABIALIZED`     | `labialized`          | `w`, `sʷː`, `ʍ`    |
| `SecondaryPlace.PALATALIZED`    | `palatalized`         | `tʲ`, `ʃᶣ`, `k̚ʲ`  |
| `SecondaryPlace.VELARIZED`      | `velarized`           | `ɫ`, `l̩ˠ`, `mˠ`   |
| `SecondaryPlace.PHARYNGEALIZED` | `pharyngealized`      | `t̪ˤ`, `bˤ`, `ɑˤː` |
| `SecondaryPlace.GLOTTALIZED`    | `glottalized`         | `æ̰ˀ`, `ɔˀ`, `yˀ`  |

#### `SoundSubtype`/`'sound subtype'` [[1]](https://en.wikipedia.org/wiki/Doubly_articulated_consonant), [[2]](https://en.wikipedia.org/wiki/Pulmonic-contour_click), [[3]](https://en.wikipedia.org/wiki/Ejective-contour_click), [[4]](https://en.wikipedia.org/wiki/Diphthong), [[5]](https://en.wikipedia.org/wiki/Triphthong)
| Value                                       | String representation          | Examples             |
| ------------------------------------------- | ------------------------------ | -------------------- |
| `SoundSubtype.SIMPLE_CONSONANT`             | `simple consonant`             | `n`, `ʑː`, `t͡ʃʲ`    |
| `SoundSubtype.DOUBLY_ARTICULATED_CONSONANT` | `doubly articulated consonant` | `ŋ͡m`, `k͡p̚`, `ɡ͡b` |
| `SoundSubtype.CONTOUR_CLICK`                | `contour click`                | `ᵏǃ͡χʼ`, `ǃ͡qʰ`      |
| `SoundSubtype.SIMPLE_VOWEL`                 | `simple vowel`                 | `a`, `ə̹`, `ɯ̟̃ᵝ`    |
| `SoundSubtype.DIPHTHONG`                    | `diphthong`                    | `ʉ͜i`, `u͡ɛ`, `e͡ɪ`  |
| `SoundSubtype.TRIPHTHONG`                   | `triphthong`                   | `œ̞͡ɐ̯͡u̯`           |

#### `SoundType`/`'sound type'`
| Value                 | String representation | Examples          |
| --------------------- | --------------------- | ----------------- |
| `SoundType.CONSONANT` | `consonant`           | `n`, `vː`, `t͡ʃʲ` |
| `SoundType.VOWEL`     | `vowel`               | `a`, `ø̯`, `ʏ̟`   |

#### `Strength`/`'strength'` [[1]](https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics)
| Value             | String representation | Examples           |
| ----------------- | --------------------- | ------------------ |
| `Strength.STRONG` | `strong`              | `t͡s͈`, `n͈`, `l͈` |
| `Strength.WEAK`   | `weak`                | `v͉`               |

#### `StressSubtype`/`'stress subtype'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals), [[2]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Stress)
| Value                                       | String representation         | Examples |
| ------------------------------------------- | ----------------------------- | -------- |
| `StressSubtype.REGULAR_PRIMARY_STRESS`      | `regular primary stress`      | `ˈ`      |
| `StressSubtype.EXTRA_STRONG_PRIMARY_STRESS` | `extra-strong primary stress` | `ˈˈ`     |
| `StressSubtype.REGULAR_SECONDARY_STRESS`    | `regular secondary stress`    | `ˌ`      |
| `StressSubtype.EXTRA_WEAK_SECONDARY_STRESS` | `extra-weak secondary stress` | `ˌˌ`     |

#### `StressType`/`'stress type'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals), [[2]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Stress)
| Value                         | String representation | Examples  |
| ----------------------------- | --------------------- | --------- |
| `StressType.PRIMARY_STRESS`   | `primary stress`      | `ˈ`, `ˈˈ` |
| `StressType.SECONDARY_STRESS` | `secondary stress`    | `ˌ`, `ˌˌ` |

#### `SuprasegmentalType`/`'suprasegmental type'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals), [[2]](https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics)
| Value                           | String representation | Examples       |
| ------------------------------- | --------------------- | -------------- |
| `SuprasegmentalType.STRESS`     | `stress`              | `ˈ`, `ˌ`, `ˈˈ` |
| `SuprasegmentalType.TONE`       | `tone`                | `˥`, `⁴`, `¹`  |
| `SuprasegmentalType.INTONATION` | `intonation`          | `↘`, `↗`       |
| `SuprasegmentalType.AIRFLOW`    | `airflow`             | `↓`, `↑`       |

#### `Syllabicity`/`'syllabicity'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation), [[2]](https://en.wiktionary.org/wiki/%E1%B5%8A)
| Value                     | String representation | Examples           |
| ------------------------- | --------------------- | ------------------ |
| `Syllabicity.SYLLABIC`    | `syllabic`            | `n̩`, `ŋ̍`, `r̩̂`  |
| `Syllabicity.NONSYLLABIC` | `nonsyllabic`         | `i̯`, `ʏ̯ː`, `ɪ̯ˑ` |
| `Syllabicity.ANAPTYCTIC`  | `anaptyctic`          | `ᵊ`                |

#### `SymbolType`/`'symbol type'`
| Value                       | String representation | Examples         |
| --------------------------- | --------------------- | ---------------- |
| `SymbolType.SOUND`          | `sound`               | `a`, `ɡʲʷ`, `ʰk` |
| `SymbolType.BREAK`          | `break`               | `.`, `-`, `‿`    |
| `SymbolType.SUPRASEGMENTAL` | `suprasegmental`      | `ˈ`, `ꜜ`, `⁻`    |

#### `Tone`/`'tone'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals), [[2]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Pitch_and_tone)
| Value                       | String representation  | Examples               |
| --------------------------- | ---------------------- | ---------------------- |
| `Tone.EXTRA_HIGH_TONE`      | `extra-high tone`      | `ɹ̩̋`, `ő`, `a̋`      |
| `Tone.HIGH_TONE`            | `high tone`            | `í`, `ɑ̃́`, `ɯ́ᵝː`    |
| `Tone.MID_TONE`             | `mid tone`             | `ā`, `ɵ̄`, `īː`      |
| `Tone.LOW_TONE`             | `low tone`             | `à`, `ù̘`, `æ̀ː`     |
| `Tone.EXTRA_LOW_TONE`       | `extra-low tone`       | `ɨ̏ː`, `ȁ`            |
| `Tone.RISING_TONE`          | `rising tone`          | `ǎ`, `ěː`, `m̩̌`     |
| `Tone.FALLING_TONE`         | `falling tone`         | `êː`, `û`, `ɔ̂`      |
| `Tone.HIGH_MID_RISING_TONE` | `high/mid rising tone` | `a᷄ː`, `a᷄`, `u᷄`      |
| `Tone.LOW_RISING_TONE`      | `low rising tone`      | `i᷅ː`, `a᷅ː`, `ɛ᷅`     |
| `Tone.HIGH_FALLING_TONE`    | `high falling tone`    | `a᷇`, `u᷇ː`, `u᷇`      |
| `Tone.LOW_MID_FALLING_TONE` | `low/mid falling tone` | `ɪ᷆`, `e᷆ː`, `ə᷆`      |
| `Tone.PEAKING_TONE`         | `peaking tone`         | `a̤᷈ː`, `e̤᷈ː`, `ṳ᷈ː` |
| `Tone.DIPPING_TONE`         | `dipping tone`         | `a᷉`                   |

#### `ToneLetter`/`'tone letter'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals)
| Value                              | String representation   | Examples         |
| ---------------------------------- | ----------------------- | ---------------- |
| `ToneLetter.HIGH_TONE_LETTER`      | `high tone letter`      | `˥`              |
| `ToneLetter.HALF_HIGH_TONE_LETTER` | `half-high tone letter` | `˦`, `˦ˀ`        |
| `ToneLetter.MID_TONE_LETTER`       | `mid tone letter`       | `˧`, `꜔`, `˧ˀ`   |
| `ToneLetter.HALF_LOW_TONE_LETTER`  | `half-low tone letter`  | `˨`, `˨ˀ`        |
| `ToneLetter.LOW_TONE_LETTER`       | `low tone letter`       | `˩`, `˩̰ˀ`, `˩̤` |

#### `ToneNumber`/`'tone number'` [[1]](https://en.wikipedia.org/wiki/Tone_number), [[2]](https://en.wiktionary.org/wiki/Template:IPA)
| Value                              | String representation   | Examples |
| ---------------------------------- | ----------------------- | -------- |
| `ToneNumber.TONE_0`                | `tone 0`                | `⁰`      |
| `ToneNumber.TONE_1`                | `tone 1`                | `¹`      |
| `ToneNumber.TONE_2`                | `tone 2`                | `²`      |
| `ToneNumber.TONE_3`                | `tone 3`                | `³`      |
| `ToneNumber.TONE_4`                | `tone 4`                | `⁴`      |
| `ToneNumber.TONE_5`                | `tone 5`                | `⁵`      |
| `ToneNumber.TONE_6`                | `tone 6`                | `⁶`      |
| `ToneNumber.TONE_7`                | `tone 7`                | `⁷`      |
| `ToneNumber.TONE_NUMBER_SEPARATOR` | `tone number separator` | `⁻`      |

#### `ToneStep`/`'tone step'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals)
| Value               | String representation | Examples |
| ------------------- | --------------------- | -------- |
| `ToneStep.UPSTEP`   | `upstep`              | `ꜛ`      |
| `ToneStep.DOWNSTEP` | `downstep`            | `ꜜ`      |

#### `ToneType`/`'tone type'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals), [[2]](https://en.wikipedia.org/wiki/Tone_number), [[3]](https://en.wiktionary.org/wiki/Template:IPA)
| Value                  | String representation | Examples      |
| ---------------------- | --------------------- | ------------- |
| `ToneType.TONE_LETTER` | `tone letter`         | `˥`, `˦`, `˨` |
| `ToneType.TONE_NUMBER` | `tone number`         | `⁵`, `¹`, `²` |
| `ToneType.TONE_STEP`   | `tone step`           | `ꜜ`, `ꜛ`      |

#### `Voicing`/`'voicing'` [[1]](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Consonants), [[2]](https://en.wikipedia.org/wiki/Voicelessness#Voiceless_vowels_and_other_sonorants)
| Value              | String representation | Examples           |
| ------------------ | --------------------- | ------------------ |
| `Voicing.VOICED`   | `voiced`              | `n`, `bˤ`, `ɡʰ`    |
| `Voicing.DEVOICED` | `devoiced`            | `u̥`, `ɯ̟̊`, `ĭ̥` |

### Feature typing and helper methods

You can iterate through all the supported features using the tuple `FEATURE_KINDS`. Feature kinds (such as `Height`, `Manner`, or `Voicing`) are all enums subclassed off of the base class `Feature`. Feature kinds themselves have the type `Type[Feature]`, aliased `FeatureKind`. The `.kind_values()` method can be called to retrieve supported string representations of the feature kind. 

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

`FeatureSet` is an alias for `frozenset[Feature]` (the return type of `IPASymbol.features()`).

```python
from ipaparser import IPASymbol
from ipaparser.features import FeatureSet, SoundType, Syllabicity


def is_syllabic(features: FeatureSet) -> bool:
    if SoundType.CONSONANT in features:
        return Syllabicity.SYLLABIC in features
    if SoundType.VOWEL in features:
        return Syllabicity.NONSYLLABIC not in features
    return False


print(is_syllabic(IPASymbol('a').features()))
```

Finally, the `.derived()` and `.extend()` methods of individual features may be called to obtain basic hierarchical relationships between features:

```python
from ipaparser.features import Place, ToneLetter

print(Place.ALVEOLAR.derived())  # get the most specific derived feature
# PlaceCategory.CORONAL

print(ToneLetter.HIGH_TONE_LETTER.extend())  # all the derived features, including the caller
# frozenset({<SuprasegmentalType.TONE: 'tone'>,
#            <ToneLetter.HIGH_TONE_LETTER: 'high tone letter'>,
#            <ToneType.TONE_LETTER: 'tone letter'>,
#            <SymbolType.SUPRASEGMENTAL: 'suprasegmental'>})
```

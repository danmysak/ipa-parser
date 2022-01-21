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

<table>
<thead>
<tr>
<th>Kind</th>
<th>Feature</th>
<th>Examples</th>
<th>Sources</th>
</tr>
</thead>
<tbody>
<tr>
<td align="center" rowspan="2"><code>Airflow</code><br><code>'airflow'</code></td>
<td><code>EGRESSIVE_AIRFLOW</code><br><code>'egressive airflow'</code></td>
<td><code>↑</code></td>
<td align="center" rowspan="2"><a href="https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics">[1]</a></td>
</tr>
<tr>
<td><code>INGRESSIVE_AIRFLOW</code><br><code>'ingressive airflow'</code></td>
<td><code>↓</code></td>
</tr>
<tr>
<td align="center" rowspan="8"><code>Articulation</code><br><code>'articulation'</code></td>
<td><code>APICAL</code><br><code>'apical'</code></td>
<td><code>s̺</code>, <code>z̺</code>, <code>ɾ̺</code></td>
<td align="center" rowspan="8"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation">[1]</a></td>
</tr>
<tr>
<td><code>LAMINAL</code><br><code>'laminal'</code></td>
<td><code>s̻</code>, <code>z̻</code>, <code>n̻</code></td>
</tr>
<tr>
<td><code>ADVANCED</code><br><code>'advanced'</code></td>
<td><code>ɯ̟ᵝ</code>, <code>o̞˖</code>, <code>ʎ̟</code></td>
</tr>
<tr>
<td><code>RETRACTED</code><br><code>'retracted'</code></td>
<td><code>a̠</code>, <code>ð̩˕˗ˠˀ</code>, <code>i̠</code></td>
</tr>
<tr>
<td><code>CENTRALIZED</code><br><code>'centralized'</code></td>
<td><code>æ̈</code>, <code>ɑ̈ː</code>, <code>ö</code></td>
</tr>
<tr>
<td><code>MID_CENTRALIZED</code><br><code>'mid-centralized'</code></td>
<td><code>e̽</code>, <code>ɯ̥̽</code>, <code>ɤ̽</code></td>
</tr>
<tr>
<td><code>RAISED</code><br><code>'raised'</code></td>
<td><code>ɛ̝</code>, <code>ʎ̥˔</code>, <code>e̝ˀ</code></td>
</tr>
<tr>
<td><code>LOWERED</code><br><code>'lowered'</code></td>
<td><code>ʏ̞</code>, <code>ò˕</code>, <code>ɛ̞̃</code></td>
</tr>
<tr>
<td align="center" rowspan="3"><code>Aspiration</code><br><code>'aspiration'</code></td>
<td><code>ASPIRATED</code><br><code>'aspirated'</code></td>
<td><code>tʰ</code>, <code>kʰː</code>, <code>ǀʰ</code></td>
<td align="center" rowspan="3"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation">[1]</a>, <a href="https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics">[2]</a></td>
</tr>
<tr>
<td><code>UNASPIRATED</code><br><code>'unaspirated'</code></td>
<td><code>ʔ˭</code>, <code>p˭</code></td>
</tr>
<tr>
<td><code>PREASPIRATED</code><br><code>'preaspirated'</code></td>
<td><code>ʰt͡s</code>, <code>ʰkʰʲ</code>, <code>ʰp</code></td>
</tr>
<tr>
<td align="center" rowspan="5"><code>Backness</code><br><code>'backness'</code></td>
<td><code>FRONT</code><br><code>'front'</code></td>
<td><code>a</code>, <code>ɛ̀ː</code>, <code>ǽ</code></td>
<td align="center" rowspan="5"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Vowels">[1]</a></td>
</tr>
<tr>
<td><code>NEAR_FRONT</code><br><code>'near-front'</code></td>
<td><code>ɪ</code>, <code>ʏ˞</code>, <code>ɪˑ</code></td>
</tr>
<tr>
<td><code>CENTRAL</code><br><code>'central'</code></td>
<td><code>ə</code>, <code>ʉ́</code>, <code>ɘ̯</code></td>
</tr>
<tr>
<td><code>NEAR_BACK</code><br><code>'near-back'</code></td>
<td><code>ʊ</code>, <code>ʊ́</code>, <code>ʊ̂</code></td>
</tr>
<tr>
<td><code>BACK</code><br><code>'back'</code></td>
<td><code>o</code>, <code>ü</code>, <code>ɯ̟̃ᵝ</code></td>
</tr>
<tr>
<td align="center" rowspan="3"><code>BacknessCategory</code><br><code>'backness category'</code></td>
<td><code>ABOUT_FRONT</code><br><code>'about front'</code></td>
<td><code>a</code>, <code>ɪ̙́</code>, <code>ʏ˞</code></td>
<td align="center" rowspan="3"></td>
</tr>
<tr>
<td><code>ABOUT_CENTRAL</code><br><code>'about central'</code></td>
<td><code>ə</code>, <code>ʉ́</code>, <code>ɘ̯</code></td>
</tr>
<tr>
<td><code>ABOUT_BACK</code><br><code>'about back'</code></td>
<td><code>o</code>, <code>ʊ̥</code>, <code>ü</code></td>
</tr>
<tr>
<td align="center" rowspan="8"><code>BreakType</code><br><code>'break type'</code></td>
<td><code>SPACE</code><br><code>'space'</code></td>
<td><code> </code></td>
<td align="center" rowspan="8"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals">[1]</a></td>
</tr>
<tr>
<td><code>HYPHEN</code><br><code>'hyphen'</code></td>
<td><code>-</code></td>
</tr>
<tr>
<td><code>LINKING</code><br><code>'linking'</code></td>
<td><code>‿</code></td>
</tr>
<tr>
<td><code>SYLLABLE_BREAK</code><br><code>'syllable break'</code></td>
<td><code>.</code></td>
</tr>
<tr>
<td><code>MINOR_BREAK</code><br><code>'minor break'</code></td>
<td><code>|</code></td>
</tr>
<tr>
<td><code>MAJOR_BREAK</code><br><code>'major break'</code></td>
<td><code>‖</code></td>
</tr>
<tr>
<td><code>EQUIVALENCE</code><br><code>'equivalence'</code></td>
<td><code>~</code>, <code>⁓</code></td>
</tr>
<tr>
<td><code>ELLIPSIS</code><br><code>'ellipsis'</code></td>
<td><code>…</code></td>
</tr>
<tr>
<td align="center" rowspan="7"><code>Height</code><br><code>'height'</code></td>
<td><code>CLOSE</code><br><code>'close'</code></td>
<td><code>i</code>, <code>ṳ̌ː</code>, <code>ʉ̀</code></td>
<td align="center" rowspan="7"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Vowels">[1]</a></td>
</tr>
<tr>
<td><code>NEAR_CLOSE</code><br><code>'near-close'</code></td>
<td><code>ɪ</code>, <code>ʏ˞</code>, <code>ʊ̯ˑ</code></td>
</tr>
<tr>
<td><code>CLOSE_MID</code><br><code>'close-mid'</code></td>
<td><code>e</code>, <code>ɤː</code>, <code>o̟</code></td>
</tr>
<tr>
<td><code>MID</code><br><code>'mid'</code></td>
<td><code>ə</code>, <code>ɚː</code>, <code>ɤ̞</code></td>
</tr>
<tr>
<td><code>OPEN_MID</code><br><code>'open-mid'</code></td>
<td><code>ɛ</code>, <code>ɔ̃ː</code>, <code>ɜ˞</code></td>
</tr>
<tr>
<td><code>NEAR_OPEN</code><br><code>'near-open'</code></td>
<td><code>ɐ</code>, <code>ǽ</code>, <code>ɐ̆</code></td>
</tr>
<tr>
<td><code>OPEN</code><br><code>'open'</code></td>
<td><code>a</code>, <code>ɒ̯̽ˀ</code>, <code>ɑ̃ː</code></td>
</tr>
<tr>
<td align="center" rowspan="3"><code>HeightCategory</code><br><code>'height category'</code></td>
<td><code>ABOUT_CLOSE</code><br><code>'about close'</code></td>
<td><code>i</code>, <code>ʏ˞</code>, <code>ʊ̯ˑ</code></td>
<td align="center" rowspan="3"></td>
</tr>
<tr>
<td><code>ABOUT_MID</code><br><code>'about mid'</code></td>
<td><code>ə</code>, <code>ɘ̯</code>, <code>ɜˑ</code></td>
</tr>
<tr>
<td><code>ABOUT_OPEN</code><br><code>'about open'</code></td>
<td><code>a</code>, <code>æːˀ</code>, <code>ɑ̆</code></td>
</tr>
<tr>
<td align="center" rowspan="2"><code>Intonation</code><br><code>'intonation'</code></td>
<td><code>GLOBAL_RISE</code><br><code>'global rise'</code></td>
<td><code>↗</code></td>
<td align="center" rowspan="2"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals">[1]</a></td>
</tr>
<tr>
<td><code>GLOBAL_FALL</code><br><code>'global fall'</code></td>
<td><code>↘</code></td>
</tr>
<tr>
<td align="center" rowspan="4"><code>Length</code><br><code>'length'</code></td>
<td><code>EXTRA_SHORT</code><br><code>'extra-short'</code></td>
<td><code>n̆</code>, <code>ø̆</code>, <code>ŏ</code></td>
<td align="center" rowspan="4"><a href="https://en.wikipedia.org/wiki/Length_(phonetics)">[1]</a></td>
</tr>
<tr>
<td><code>HALF_LONG</code><br><code>'half-long'</code></td>
<td><code>äˑ</code>, <code>e̞ˑ</code>, <code>øˑ</code></td>
</tr>
<tr>
<td><code>LONG</code><br><code>'long'</code></td>
<td><code>aː</code>, <code>l̺ː</code>, <code>ɞː</code></td>
</tr>
<tr>
<td><code>EXTRA_LONG</code><br><code>'extra-long'</code></td>
<td><code>øːˑ</code>, <code>ɛːː</code>, <code>ɨˤːː</code></td>
</tr>
<tr>
<td align="center" rowspan="12"><code>Manner</code><br><code>'manner'</code></td>
<td><code>AFFRICATE</code><br><code>'affricate'</code></td>
<td><code>t͡s</code>, <code>d͡zː</code>, <code>q͡χʷ</code></td>
<td align="center" rowspan="12"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Consonants">[1]</a></td>
</tr>
<tr>
<td><code>APPROXIMANT</code><br><code>'approximant'</code></td>
<td><code>l</code>, <code>w̥ʰ</code>, <code>ɻ̊</code></td>
</tr>
<tr>
<td><code>FRICATIVE</code><br><code>'fricative'</code></td>
<td><code>s</code>, <code>ʂ͜ʲ</code>, <code>xʼ</code></td>
</tr>
<tr>
<td><code>LATERAL</code><br><code>'lateral'</code></td>
<td><code>l</code>, <code>t͡ɬʼ</code>, <code>ŋ͜ǁ</code></td>
</tr>
<tr>
<td><code>NASAL</code><br><code>'nasal'</code></td>
<td><code>n</code>, <code>mʷ</code>, <code>ɳ̩</code></td>
</tr>
<tr>
<td><code>SIBILANT</code><br><code>'sibilant'</code></td>
<td><code>s</code>, <code>ʑː</code>, <code>t͡ʃʲ</code></td>
</tr>
<tr>
<td><code>STOP</code><br><code>'stop'</code></td>
<td><code>k</code>, <code>tʲʰː</code>, <code>qˤ</code></td>
</tr>
<tr>
<td><code>TAP_FLAP</code><br><code>'tap/flap'</code></td>
<td><code>ɾ</code>, <code>ɽ̃</code>, <code>ɺ</code></td>
</tr>
<tr>
<td><code>TRILL</code><br><code>'trill'</code></td>
<td><code>r</code>, <code>ʀ̟</code>, <code>ʙ</code></td>
</tr>
<tr>
<td><code>CLICK</code><br><code>'click'</code></td>
<td><code>ǃ</code>, <code>ᵑǀʱ</code>, <code>ǁ</code></td>
</tr>
<tr>
<td><code>EJECTIVE</code><br><code>'ejective'</code></td>
<td><code>tʼ</code>, <code>ɬˤʼ</code>, <code>kʼʷ</code></td>
</tr>
<tr>
<td><code>IMPLOSIVE</code><br><code>'implosive'</code></td>
<td><code>ɓ</code>, <code>ʄ</code>, <code>ɗʲ</code></td>
</tr>
<tr>
<td align="center" rowspan="3"><code>Phonation</code><br><code>'phonation'</code></td>
<td><code>BREATHY</code><br><code>'breathy'</code></td>
<td><code>bʱ</code>, <code>ṳ̌</code>, <code>ᵑǀʱ</code></td>
<td align="center" rowspan="3"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation">[1]</a>, <a href="https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics">[2]</a></td>
</tr>
<tr>
<td><code>CREAKY</code><br><code>'creaky'</code></td>
<td><code>æ̰ˀ</code>, <code>ɑ̰́ː</code>, <code>j̰</code></td>
</tr>
<tr>
<td><code>WHISPERY</code><br><code>'whispery'</code></td>
<td><code>ạ</code>, <code>ạ̀</code>, <code>x̣</code></td>
</tr>
<tr>
<td align="center" rowspan="12"><code>Place</code><br><code>'place'</code></td>
<td><code>BILABIAL</code><br><code>'bilabial'</code></td>
<td><code>m</code>, <code>b̥ˀ</code>, <code>p͡f</code></td>
<td align="center" rowspan="12"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Consonants">[1]</a></td>
</tr>
<tr>
<td><code>LABIODENTAL</code><br><code>'labiodental'</code></td>
<td><code>f</code>, <code>ᶬv</code>, <code>ʋ̥</code></td>
</tr>
<tr>
<td><code>LINGUOLABIAL</code><br><code>'linguolabial'</code></td>
<td><code>n̼</code>, <code>θ̼</code></td>
</tr>
<tr>
<td><code>DENTAL</code><br><code>'dental'</code></td>
<td><code>t̪</code>, <code>ðˠ</code>, <code>ɡ̊ǀ</code></td>
</tr>
<tr>
<td><code>ALVEOLAR</code><br><code>'alveolar'</code></td>
<td><code>n</code>, <code>t͜ɬ</code>, <code>lʱ</code></td>
</tr>
<tr>
<td><code>POSTALVEOLAR</code><br><code>'postalveolar'</code></td>
<td><code>ʃ</code>, <code>d͡ʒʲ</code>, <code>t̠̚</code></td>
</tr>
<tr>
<td><code>RETROFLEX</code><br><code>'retroflex'</code></td>
<td><code>ʂ</code>, <code>ʈⁿ</code>, <code>ɽʷ</code></td>
</tr>
<tr>
<td><code>PALATAL</code><br><code>'palatal'</code></td>
<td><code>j</code>, <code>ɟʱ</code>, <code>kǂʰ</code></td>
</tr>
<tr>
<td><code>VELAR</code><br><code>'velar'</code></td>
<td><code>k</code>, <code>ɡ̞</code>, <code>xʼ</code></td>
</tr>
<tr>
<td><code>UVULAR</code><br><code>'uvular'</code></td>
<td><code>ʁ</code>, <code>q͡χʷ</code>, <code>ʀ̥</code></td>
</tr>
<tr>
<td><code>PHARYNGEAL_EPIGLOTTAL</code><br><code>'pharyngeal/epiglottal'</code></td>
<td><code>ħ</code>, <code>ʕː</code>, <code>ħʷ</code></td>
</tr>
<tr>
<td><code>GLOTTAL</code><br><code>'glottal'</code></td>
<td><code>ʔ</code>, <code>ɦʲ</code>, <code>hː</code></td>
</tr>
<tr>
<td align="center" rowspan="4"><code>PlaceCategory</code><br><code>'place category'</code></td>
<td><code>LABIAL</code><br><code>'labial'</code></td>
<td><code>m</code>, <code>ᶬv</code>, <code>b̥ˀ</code></td>
<td align="center" rowspan="4"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Consonants">[1]</a></td>
</tr>
<tr>
<td><code>CORONAL</code><br><code>'coronal'</code></td>
<td><code>n</code>, <code>t͡ʃʲ</code>, <code>ɻ̊</code></td>
</tr>
<tr>
<td><code>DORSAL</code><br><code>'dorsal'</code></td>
<td><code>k</code>, <code>q͡χʷ</code>, <code>ʎ̥˔</code></td>
</tr>
<tr>
<td><code>LARYNGEAL</code><br><code>'laryngeal'</code></td>
<td><code>ʔ</code>, <code>ʕː</code>, <code>h̃</code></td>
</tr>
<tr>
<td align="center" rowspan="6"><code>Release</code><br><code>'release'</code></td>
<td><code>NO_AUDIBLE_RELEASE</code><br><code>'no audible release'</code></td>
<td><code>t̚</code>, <code>ʔ̚</code>, <code>d̪̚</code></td>
<td align="center" rowspan="6"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation">[1]</a></td>
</tr>
<tr>
<td><code>NASAL_RELEASE</code><br><code>'nasal release'</code></td>
<td><code>tⁿ</code>, <code>t̪ⁿ</code>, <code>ʈⁿ</code></td>
</tr>
<tr>
<td><code>LATERAL_RELEASE</code><br><code>'lateral release'</code></td>
<td><code>tˡ</code>, <code>bˡ</code>, <code>ᵐbˡ</code></td>
</tr>
<tr>
<td><code>VOICELESS_DENTAL_FRICATIVE_RELEASE</code><br><code>'voiceless dental fricative release'</code></td>
<td><code>tᶿ</code></td>
</tr>
<tr>
<td><code>VOICELESS_ALVEOLAR_SIBILANT_FRICATIVE_RELEASE</code><br><code>'voiceless alveolar sibilant fricative release'</code></td>
<td><code>tˢ</code>, <code>kˢ</code>, <code>tˢʰ</code></td>
</tr>
<tr>
<td><code>VOICELESS_VELAR_FRICATIVE_RELEASE</code><br><code>'voiceless velar fricative release'</code></td>
<td><code>kˣ</code></td>
</tr>
<tr>
<td align="center" rowspan="1"><code>Roundedness</code><br><code>'roundedness'</code></td>
<td><code>ROUNDED</code><br><code>'rounded'</code></td>
<td><code>o</code>, <code>ṳ̌ː</code>, <code>ʉ̀</code></td>
<td align="center" rowspan="1"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Vowels">[1]</a></td>
</tr>
<tr>
<td align="center" rowspan="4"><code>RoundednessModifier</code><br><code>'roundedness modifier'</code></td>
<td><code>MORE_ROUNDED</code><br><code>'more rounded'</code></td>
<td><code>ʌ̹</code>, <code>ə̹</code>, <code>ɔ̹</code></td>
<td align="center" rowspan="4"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation">[1]</a>, <a href="https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics">[2]</a></td>
</tr>
<tr>
<td><code>LESS_ROUNDED</code><br><code>'less rounded'</code></td>
<td><code>w̜</code>, <code>ɒ̜˔ː</code>, <code>ɔ̜ˑ</code></td>
</tr>
<tr>
<td><code>COMPRESSED</code><br><code>'compressed'</code></td>
<td><code>ɯ̟ᵝ</code>, <code>ɨ̃ᵝ</code>, <code>ɰᵝ</code></td>
</tr>
<tr>
<td><code>LABIAL_SPREADING</code><br><code>'labial spreading'</code></td>
<td><code>u͍</code>, <code>u͍ː</code>, <code>w͍</code></td>
</tr>
<tr>
<td align="center" rowspan="8"><code>SecondaryModifier</code><br><code>'secondary modifier'</code></td>
<td><code>ADVANCED_TONGUE_ROOT</code><br><code>'advanced tongue root'</code></td>
<td><code>ɨ̘</code>, <code>ɤ̘</code>, <code>í̘ː</code></td>
<td align="center" rowspan="8"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation">[1]</a>, <a href="https://en.wikipedia.org/wiki/Prenasalized_consonant">[2]</a>, <a href="https://en.wikipedia.org/wiki/Pre-stopped_consonant">[3]</a>, <a href="https://linguistics.ucla.edu/people/keating/Keating_JIPA_diacritics_accepted_complete_Feb2019.pdf">[4]</a>, <a href="https://en.wikipedia.org/wiki/Glottalized_click#Preglottalized_nasal_clicks">[5]</a></td>
</tr>
<tr>
<td><code>RETRACTED_TONGUE_ROOT</code><br><code>'retracted tongue root'</code></td>
<td><code>ɪ̙̞</code>, <code>ɒ̙̀</code>, <code>ʊ̙́</code></td>
</tr>
<tr>
<td><code>R_COLORED</code><br><code>'r-colored'</code></td>
<td><code>ɚ</code>, <code>ɝˑ</code>, <code>ɑ˞</code></td>
</tr>
<tr>
<td><code>NASALIZED</code><br><code>'nasalized'</code></td>
<td><code>ĩ</code>, <code>õ̤</code>, <code>ɯ̟̃ᵝ</code></td>
</tr>
<tr>
<td><code>PRENASALIZED</code><br><code>'prenasalized'</code></td>
<td><code>ⁿdˠ</code>, <code>n͡t</code>, <code>ᶬv</code></td>
</tr>
<tr>
<td><code>VOICELESSLY_PRENASALIZED</code><br><code>'voicelessly prenasalized'</code></td>
<td><code>m̥͡bʷ</code></td>
</tr>
<tr>
<td><code>PRESTOPPED</code><br><code>'prestopped'</code></td>
<td><code>ᵈn</code>, <code>ᵇm</code>, <code>ᵈl</code></td>
</tr>
<tr>
<td><code>PREGLOTTALIZED</code><br><code>'preglottalized'</code></td>
<td><code>ˀt</code>, <code>ˀd</code></td>
</tr>
<tr>
<td align="center" rowspan="5"><code>SecondaryPlace</code><br><code>'secondary place'</code></td>
<td><code>LABIALIZED</code><br><code>'labialized'</code></td>
<td><code>w</code>, <code>sʷː</code>, <code>ʍ</code></td>
<td align="center" rowspan="5"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation">[1]</a></td>
</tr>
<tr>
<td><code>PALATALIZED</code><br><code>'palatalized'</code></td>
<td><code>tʲ</code>, <code>ʃᶣ</code>, <code>k̚ʲ</code></td>
</tr>
<tr>
<td><code>VELARIZED</code><br><code>'velarized'</code></td>
<td><code>ɫ</code>, <code>l̩ˠ</code>, <code>mˠ</code></td>
</tr>
<tr>
<td><code>PHARYNGEALIZED</code><br><code>'pharyngealized'</code></td>
<td><code>t̪ˤ</code>, <code>bˤ</code>, <code>ɑˤː</code></td>
</tr>
<tr>
<td><code>GLOTTALIZED</code><br><code>'glottalized'</code></td>
<td><code>æ̰ˀ</code>, <code>ɔˀ</code>, <code>yˀ</code></td>
</tr>
<tr>
<td align="center" rowspan="6"><code>SoundSubtype</code><br><code>'sound subtype'</code></td>
<td><code>SIMPLE_CONSONANT</code><br><code>'simple consonant'</code></td>
<td><code>n</code>, <code>ʑː</code>, <code>t͡ʃʲ</code></td>
<td align="center" rowspan="6"><a href="https://en.wikipedia.org/wiki/Doubly_articulated_consonant">[1]</a>, <a href="https://en.wikipedia.org/wiki/Pulmonic-contour_click">[2]</a>, <a href="https://en.wikipedia.org/wiki/Ejective-contour_click">[3]</a>, <a href="https://en.wikipedia.org/wiki/Diphthong">[4]</a>, <a href="https://en.wikipedia.org/wiki/Triphthong">[5]</a></td>
</tr>
<tr>
<td><code>DOUBLY_ARTICULATED_CONSONANT</code><br><code>'doubly articulated consonant'</code></td>
<td><code>ŋ͡m</code>, <code>k͡p̚</code>, <code>ɡ͡b</code></td>
</tr>
<tr>
<td><code>CONTOUR_CLICK</code><br><code>'contour click'</code></td>
<td><code>ᵏǃ͡χʼ</code>, <code>ǃ͡qʰ</code></td>
</tr>
<tr>
<td><code>SIMPLE_VOWEL</code><br><code>'simple vowel'</code></td>
<td><code>a</code>, <code>ə̹</code>, <code>ɯ̟̃ᵝ</code></td>
</tr>
<tr>
<td><code>DIPHTHONG</code><br><code>'diphthong'</code></td>
<td><code>ʉ͜i</code>, <code>u͡ɛ</code>, <code>e͡ɪ</code></td>
</tr>
<tr>
<td><code>TRIPHTHONG</code><br><code>'triphthong'</code></td>
<td><code>œ̞͡ɐ̯͡u̯</code></td>
</tr>
<tr>
<td align="center" rowspan="2"><code>SoundType</code><br><code>'sound type'</code></td>
<td><code>CONSONANT</code><br><code>'consonant'</code></td>
<td><code>n</code>, <code>k͡p̚</code>, <code>ᵏǃ͡χʼ</code></td>
<td align="center" rowspan="2"></td>
</tr>
<tr>
<td><code>VOWEL</code><br><code>'vowel'</code></td>
<td><code>a</code>, <code>ɔ͜y</code>, <code>ø̯</code></td>
</tr>
<tr>
<td align="center" rowspan="2"><code>Strength</code><br><code>'strength'</code></td>
<td><code>STRONG</code><br><code>'strong'</code></td>
<td><code>t͡s͈</code>, <code>n͈</code>, <code>l͈</code></td>
<td align="center" rowspan="2"><a href="https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics">[1]</a></td>
</tr>
<tr>
<td><code>WEAK</code><br><code>'weak'</code></td>
<td><code>v͉</code></td>
</tr>
<tr>
<td align="center" rowspan="4"><code>StressSubtype</code><br><code>'stress subtype'</code></td>
<td><code>REGULAR_PRIMARY_STRESS</code><br><code>'regular primary stress'</code></td>
<td><code>ˈ</code></td>
<td align="center" rowspan="4"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals">[1]</a>, <a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Stress">[2]</a></td>
</tr>
<tr>
<td><code>EXTRA_STRONG_PRIMARY_STRESS</code><br><code>'extra-strong primary stress'</code></td>
<td><code>ˈˈ</code></td>
</tr>
<tr>
<td><code>REGULAR_SECONDARY_STRESS</code><br><code>'regular secondary stress'</code></td>
<td><code>ˌ</code></td>
</tr>
<tr>
<td><code>EXTRA_WEAK_SECONDARY_STRESS</code><br><code>'extra-weak secondary stress'</code></td>
<td><code>ˌˌ</code></td>
</tr>
<tr>
<td align="center" rowspan="2"><code>StressType</code><br><code>'stress type'</code></td>
<td><code>PRIMARY_STRESS</code><br><code>'primary stress'</code></td>
<td><code>ˈ</code>, <code>ˈˈ</code></td>
<td align="center" rowspan="2"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals">[1]</a>, <a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Stress">[2]</a></td>
</tr>
<tr>
<td><code>SECONDARY_STRESS</code><br><code>'secondary stress'</code></td>
<td><code>ˌ</code>, <code>ˌˌ</code></td>
</tr>
<tr>
<td align="center" rowspan="4"><code>SuprasegmentalType</code><br><code>'suprasegmental type'</code></td>
<td><code>STRESS</code><br><code>'stress'</code></td>
<td><code>ˈ</code>, <code>ˌ</code>, <code>ˈˈ</code></td>
<td align="center" rowspan="4"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals">[1]</a>, <a href="https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics">[2]</a></td>
</tr>
<tr>
<td><code>TONE</code><br><code>'tone'</code></td>
<td><code>˥</code>, <code>⁴</code>, <code>¹</code></td>
</tr>
<tr>
<td><code>INTONATION</code><br><code>'intonation'</code></td>
<td><code>↘</code>, <code>↗</code></td>
</tr>
<tr>
<td><code>AIRFLOW</code><br><code>'airflow'</code></td>
<td><code>↓</code>, <code>↑</code></td>
</tr>
<tr>
<td align="center" rowspan="3"><code>Syllabicity</code><br><code>'syllabicity'</code></td>
<td><code>SYLLABIC</code><br><code>'syllabic'</code></td>
<td><code>n̩</code>, <code>ŋ̍</code>, <code>r̩̂</code></td>
<td align="center" rowspan="3"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation">[1]</a>, <a href="https://en.wiktionary.org/wiki/%E1%B5%8A">[2]</a></td>
</tr>
<tr>
<td><code>NONSYLLABIC</code><br><code>'nonsyllabic'</code></td>
<td><code>i̯</code>, <code>ʏ̯ː</code>, <code>ɪ̯ˑ</code></td>
</tr>
<tr>
<td><code>ANAPTYCTIC</code><br><code>'anaptyctic'</code></td>
<td><code>ᵊ</code></td>
</tr>
<tr>
<td align="center" rowspan="3"><code>SymbolType</code><br><code>'symbol type'</code></td>
<td><code>SOUND</code><br><code>'sound'</code></td>
<td><code>a</code>, <code>ɡʲʷ</code>, <code>ʰk</code></td>
<td align="center" rowspan="3"></td>
</tr>
<tr>
<td><code>BREAK</code><br><code>'break'</code></td>
<td><code>.</code>, <code>-</code>, <code>‿</code></td>
</tr>
<tr>
<td><code>SUPRASEGMENTAL</code><br><code>'suprasegmental'</code></td>
<td><code>ˈ</code>, <code>ꜜ</code>, <code>⁻</code></td>
</tr>
<tr>
<td align="center" rowspan="13"><code>Tone</code><br><code>'tone'</code></td>
<td><code>EXTRA_HIGH_TONE</code><br><code>'extra-high tone'</code></td>
<td><code>ɹ̩̋</code>, <code>ő</code>, <code>a̋</code></td>
<td align="center" rowspan="13"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals">[1]</a>, <a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Pitch_and_tone">[2]</a></td>
</tr>
<tr>
<td><code>HIGH_TONE</code><br><code>'high tone'</code></td>
<td><code>í</code>, <code>ɑ̃́</code>, <code>ɯ́ᵝː</code></td>
</tr>
<tr>
<td><code>MID_TONE</code><br><code>'mid tone'</code></td>
<td><code>ā</code>, <code>ɵ̄</code>, <code>īː</code></td>
</tr>
<tr>
<td><code>LOW_TONE</code><br><code>'low tone'</code></td>
<td><code>à</code>, <code>ù̘</code>, <code>æ̀ː</code></td>
</tr>
<tr>
<td><code>EXTRA_LOW_TONE</code><br><code>'extra-low tone'</code></td>
<td><code>ɨ̏ː</code>, <code>ȁ</code></td>
</tr>
<tr>
<td><code>RISING_TONE</code><br><code>'rising tone'</code></td>
<td><code>ǎ</code>, <code>ěː</code>, <code>m̩̌</code></td>
</tr>
<tr>
<td><code>FALLING_TONE</code><br><code>'falling tone'</code></td>
<td><code>êː</code>, <code>û</code>, <code>ɔ̂</code></td>
</tr>
<tr>
<td><code>HIGH_MID_RISING_TONE</code><br><code>'high/mid rising tone'</code></td>
<td><code>a᷄ː</code>, <code>a᷄</code>, <code>u᷄</code></td>
</tr>
<tr>
<td><code>LOW_RISING_TONE</code><br><code>'low rising tone'</code></td>
<td><code>i᷅ː</code>, <code>a᷅ː</code>, <code>ɛ᷅</code></td>
</tr>
<tr>
<td><code>HIGH_FALLING_TONE</code><br><code>'high falling tone'</code></td>
<td><code>a᷇</code>, <code>u᷇ː</code>, <code>u᷇</code></td>
</tr>
<tr>
<td><code>LOW_MID_FALLING_TONE</code><br><code>'low/mid falling tone'</code></td>
<td><code>ɪ᷆</code>, <code>e᷆ː</code>, <code>ə᷆</code></td>
</tr>
<tr>
<td><code>PEAKING_TONE</code><br><code>'peaking tone'</code></td>
<td><code>a̤᷈ː</code>, <code>e̤᷈ː</code>, <code>ṳ᷈ː</code></td>
</tr>
<tr>
<td><code>DIPPING_TONE</code><br><code>'dipping tone'</code></td>
<td><code>a᷉</code></td>
</tr>
<tr>
<td align="center" rowspan="5"><code>ToneLetter</code><br><code>'tone letter'</code></td>
<td><code>HIGH_TONE_LETTER</code><br><code>'high tone letter'</code></td>
<td><code>˥</code></td>
<td align="center" rowspan="5"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals">[1]</a></td>
</tr>
<tr>
<td><code>HALF_HIGH_TONE_LETTER</code><br><code>'half-high tone letter'</code></td>
<td><code>˦</code>, <code>˦ˀ</code></td>
</tr>
<tr>
<td><code>MID_TONE_LETTER</code><br><code>'mid tone letter'</code></td>
<td><code>˧</code>, <code>꜔</code>, <code>˧ˀ</code></td>
</tr>
<tr>
<td><code>HALF_LOW_TONE_LETTER</code><br><code>'half-low tone letter'</code></td>
<td><code>˨</code>, <code>˨ˀ</code></td>
</tr>
<tr>
<td><code>LOW_TONE_LETTER</code><br><code>'low tone letter'</code></td>
<td><code>˩</code>, <code>˩̰ˀ</code>, <code>˩̤</code></td>
</tr>
<tr>
<td align="center" rowspan="9"><code>ToneNumber</code><br><code>'tone number'</code></td>
<td><code>TONE_0</code><br><code>'tone 0'</code></td>
<td><code>⁰</code></td>
<td align="center" rowspan="9"><a href="https://en.wikipedia.org/wiki/Tone_number">[1]</a>, <a href="https://en.wiktionary.org/wiki/Template:IPA">[2]</a></td>
</tr>
<tr>
<td><code>TONE_1</code><br><code>'tone 1'</code></td>
<td><code>¹</code></td>
</tr>
<tr>
<td><code>TONE_2</code><br><code>'tone 2'</code></td>
<td><code>²</code></td>
</tr>
<tr>
<td><code>TONE_3</code><br><code>'tone 3'</code></td>
<td><code>³</code></td>
</tr>
<tr>
<td><code>TONE_4</code><br><code>'tone 4'</code></td>
<td><code>⁴</code></td>
</tr>
<tr>
<td><code>TONE_5</code><br><code>'tone 5'</code></td>
<td><code>⁵</code></td>
</tr>
<tr>
<td><code>TONE_6</code><br><code>'tone 6'</code></td>
<td><code>⁶</code></td>
</tr>
<tr>
<td><code>TONE_7</code><br><code>'tone 7'</code></td>
<td><code>⁷</code></td>
</tr>
<tr>
<td><code>TONE_NUMBER_SEPARATOR</code><br><code>'tone number separator'</code></td>
<td><code>⁻</code></td>
</tr>
<tr>
<td align="center" rowspan="2"><code>ToneStep</code><br><code>'tone step'</code></td>
<td><code>UPSTEP</code><br><code>'upstep'</code></td>
<td><code>ꜛ</code></td>
<td align="center" rowspan="2"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals">[1]</a></td>
</tr>
<tr>
<td><code>DOWNSTEP</code><br><code>'downstep'</code></td>
<td><code>ꜜ</code></td>
</tr>
<tr>
<td align="center" rowspan="3"><code>ToneType</code><br><code>'tone type'</code></td>
<td><code>TONE_LETTER</code><br><code>'tone letter'</code></td>
<td><code>˥</code>, <code>˦</code>, <code>˨</code></td>
<td align="center" rowspan="3"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals">[1]</a>, <a href="https://en.wikipedia.org/wiki/Tone_number">[2]</a>, <a href="https://en.wiktionary.org/wiki/Template:IPA">[3]</a></td>
</tr>
<tr>
<td><code>TONE_NUMBER</code><br><code>'tone number'</code></td>
<td><code>⁵</code>, <code>¹</code>, <code>²</code></td>
</tr>
<tr>
<td><code>TONE_STEP</code><br><code>'tone step'</code></td>
<td><code>ꜜ</code>, <code>ꜛ</code></td>
</tr>
<tr>
<td align="center" rowspan="2"><code>Voicing</code><br><code>'voicing'</code></td>
<td><code>VOICED</code><br><code>'voiced'</code></td>
<td><code>n</code>, <code>bˤ</code>, <code>ɡʰ</code></td>
<td align="center" rowspan="2"><a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Consonants">[1]</a>, <a href="https://en.wikipedia.org/wiki/Voicelessness#Voiceless_vowels_and_other_sonorants">[2]</a></td>
</tr>
<tr>
<td><code>DEVOICED</code><br><code>'devoiced'</code></td>
<td><code>u̥</code>, <code>ɯ̟̊</code>, <code>ĭ̥</code></td>
</tr>
</tbody>
</table>

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

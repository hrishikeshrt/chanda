# Test Suite

This directory contains comprehensive tests for the Chanda library.

## Test Files

### `test_aksharagana_vrtta.py`
Comprehensive pytest-based test suite for Akṣara-gaṇa-vṛtta (syllable-based meters):
- **Meter identification**: Tests for all major meters (Śālinī, Indravajrā, Vasantatilakā, etc.)
- **Sama-vṛtta**: Meters with identical padas
- **Ardhasama/Viṣama-vṛtta**: Meters with varying padas
- **Verse analysis**: Full verse identification and scoring
- **Core features**: Laghu-Guru marking, gana conversion
- **Fuzzy matching**: Similarity-based meter suggestions
- **Edge cases**: Empty input, whitespace, very long lines
- **Multi-script support**: Devanagari, IAST, and other schemes
- **Output format**: Result structure validation

### `test_matra_vrtta.py`
Specialized test script for Mātrā-vṛtta (mātrā-based meters):
- Āryā meter identification (12-18-12-15 pattern)
- Āryāgīti identification (12-12-20-20 pattern)
- Gīti identification (12-18-12-18 pattern)
- Mātrā counting accuracy
- Pattern matching and verification
- Edge cases and error handling

## Running Tests

### Run all tests with pytest
```bash
# From project root
make test

# Or directly with pytest
pytest

# Verbose output
pytest -v

# Specific test file
pytest tests/test_aksharagana_vrtta.py

# Specific test
pytest tests/test_aksharagana_vrtta.py::TestMeterIdentification::test_indravajra_identification
```

### Run with coverage
```bash
make coverage
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run mātrā-vṛtta tests standalone
```bash
# From project root
python tests/test_matra_vrtta.py

# Or with pytest
pytest tests/test_matra_vrtta.py -v
```

## Test Examples

The test suite includes examples from classical Sanskrit texts:

### Śālinī
```
माता रामो मत्पिता रामचन्द्रः
स्वामी रामो मत्सखा रामचन्द्रः।
सर्वस्वं मे रामचन्द्रो दयालुर्
नान्यं‌ जाने नैव जाने न जाने॥
```

### Indravajrā
```
लोकाभिरामं रणरङ्गधीरं
राजीवनेत्रं रघुवंशनाथम्।
कारुण्यरूपं करुणाकरं तं
श्रीरामचन्द्रं शरणं प्रपद्ये॥
```

### Vasantatilakā
```
योऽन्तः प्रविश्य मम वाचमिमां प्रसुप्तां
सञ्जीवयत्यखिलशक्तिधरः स्वधाम्ना।
अन्यांश्च हस्तचरणश्रवणत्वगादीन्
प्राणान्नमो भगवते पुरुषाय तुभ्यम्॥
```

### Bhujaṅgaprayāta
```
नमस्ते सदा वत्सले मातृभूमे
त्वया हिन्दुभूमे सुखं वर्धितोऽहम्।
महामङ्गले पुण्यभूमे त्वदर्थे
पतत्वेष कायो नमस्ते नमस्ते॥
```

### Śārdūlavikrīḍita
```
विद्या नाम नरस्य रूपमधिकं प्रच्छन्नगुप्तं धनम्
विद्या भोगकरी यशः सुखकरी विद्या गुरूणां गुरुः।
विद्या बन्धुजनो विदेशगमने विद्या परा देवता
विद्या राजसु पूज्यते न हि धनं विद्याविहीनः पशुः॥
```

## Writing New Tests

### Test Structure
```python
import pytest
from chanda import analyze_line

def test_new_meter():
    """Test description"""
    line = "Sanskrit text here"
    result = analyze_line(line)

    assert result.found
    assert any(name == 'meter_name' for name, _ in result.chanda)
```

### Using Fixtures
```python
@pytest.fixture
def chanda():
    from chanda import Chanda
    from chanda.utils import get_default_data_path
    return Chanda(get_default_data_path())

def test_with_fixture(chanda):
    syllables, lg = chanda.mark_syllable_weights("धर्म")
    assert len(lg) > 0
```

## Test Coverage Goals

- **Core functionality**: 80%+ coverage
- **Edge cases**: Comprehensive handling
- **All major meters**: At least one test per category
- **Error handling**: Graceful failure tests

## Continuous Integration

Tests should pass before:
- Committing code
- Creating pull requests
- Publishing to PyPI

Run the full test suite:
```bash
make check
```

This runs:
- Format checking (black)
- Linting (flake8)
- All tests (pytest)

For optional type checking:
```bash
make check-all
```

## Troubleshooting

### Tests fail with import errors
```bash
# Install package in development mode
make dev-install
```

### Tests fail with missing data files
```bash
# Verify data files are present
ls -la chanda/data/
```

### Slow test execution
```bash
# Run with multiple cores
pytest -n auto
```

## Contributing Tests

When adding new features:
1. Write tests first (TDD)
2. Ensure tests pass locally
3. Add test documentation
4. Update this README if needed

---

For more information, see the main [README.md](../README.md) and [PUBLISHING.md](../PUBLISHING.md).

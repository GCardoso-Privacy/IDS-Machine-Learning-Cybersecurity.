import os
import pytest
import hashlib
from baixar_dados import verify_hash

# Since the miner logic was split, we test verify_hash from baseline/miner
# Let's mock a file and hash to test the specific logic.

@pytest.fixture
def dummy_file(tmp_path):
    """Creates a temporary file with known content to test hashing."""
    test_file = tmp_path / "test_data.zip"
    content = b"cybersecurity_data_test_123"
    test_file.write_bytes(content)
    
    # Calculate expected hash for this specific byte string
    expected_hash = hashlib.sha256(content).hexdigest()
    return str(test_file), expected_hash

def test_verify_hash_success(dummy_file):
    """Test that verify_hash returns True for a valid file and matching hash."""
    file_path, expected_hash = dummy_file
    result = verify_hash(file_path, expected_hash)
    assert result is True

def test_verify_hash_failure(dummy_file):
    """Test that verify_hash returns False for a mismatched hash."""
    file_path, _ = dummy_file
    bad_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    result = verify_hash(file_path, bad_hash)
    assert result is False

def test_verify_hash_file_not_found():
    """Test behavior when file does not exist."""
    with pytest.raises(FileNotFoundError):
        verify_hash("non_existent_file.zip", "somehash")

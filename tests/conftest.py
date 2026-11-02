"""Shared platform-capability fixtures."""

import pytest


@pytest.fixture
def symlink_supported(tmp_path):
    """Windows developers may lack symlink privileges; CI runners must have them."""
    import os
    link = tmp_path / "symlink-probe"
    try:
        link.symlink_to(tmp_path, target_is_directory=True)
    except OSError as e:
        if getattr(e, "winerror", None) == 1314 and not os.environ.get("CI"):
            pytest.skip("Windows symlink privilege is unavailable")
        raise
    link.unlink()

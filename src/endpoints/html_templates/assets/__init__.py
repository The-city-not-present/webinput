# Shared, skin-agnostic page assets: the base CSS and normalize CSS reused by
# every skin. Skin-specific assets (widget styles, the submit JS, etc.) live
# inside each skin's own assets/ package.

from .common_css import common_css
from .normalize_css import normalize_css

"""公開時だけ有効にする合言葉判定。未設定のときは従来どおり入れる。"""

import hmac
from typing import Optional


def decide_access(configured_password: Optional[str], provided_password: Optional[str]) -> str:
    if configured_password is None or configured_password == "":
        return "open"
    if provided_password is None:
        return "deny"
    if hmac.compare_digest(configured_password, provided_password):
        return "ok"
    return "deny"


def require_access() -> None:
    import os
    import streamlit as st

    configured = os.environ.get("APP_ACCESS_PASSWORD") or ""
    if not configured:
        return
    if st.session_state.get("app_access_ok"):
        return

    st.title("合言葉")
    st.caption("この環境では、入室用の合言葉が設定されています。")
    provided = st.text_input("合言葉", type="password")
    if st.button("入室"):
        if decide_access(configured, provided) == "ok":
            st.session_state.app_access_ok = True
            st.rerun()
        else:
            st.error("合言葉が違います")
    st.stop()

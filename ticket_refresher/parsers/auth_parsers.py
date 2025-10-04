from typing import Optional

def parse_username_from_user_anchor(anchor_ele) -> Optional[str]:
    """Extrai o nome exibido no topo quando logado."""
    if not anchor_ele:
        return None
    # O <a ng-show="User"> contém um <span class="ng-binding"> com o nome
    span = anchor_ele.ele('xpath:.//span[contains(@class,"ng-binding")]')
    if span:
        txt = (span.text or "").strip()
        return txt or None
    return None

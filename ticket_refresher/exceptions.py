class AutomationError(Exception):
    """Erro genérico de automação."""


class LoginFailedError(AutomationError):
    """Falha no login."""


class ElementNotFoundError(AutomationError):
    """Elemento esperado não encontrado."""


class NavigationError(AutomationError):
    """Falha ao navegar para uma URL."""


class PaymentFlowError(AutomationError):
    """Erro ao gerar/validar o fluxo de pagamento (QR)."""

"""Авторизация iModern с проверкой валидации и отказов."""

from core.dto import AuthCase

AUTH_CASES = [
    AuthCase("AUTH-01", "Вход по email", "email", "existing", "correct"),
    AuthCase("AUTH-02", "Пустой email", "email", "empty", "sample", "required_email"),
    AuthCase("AUTH-03", "Пустой пароль", "email", "existing", "empty", "required_password"),
    AuthCase("AUTH-04", "Неверный формат email", "email", "invalid_email", "sample", "rejected"),
    AuthCase(
        "AUTH-05", "Несуществующий email", "email", "unknown", "sample", "rejected",
    ),
    AuthCase(
        "AUTH-06", "Существующий email и неверный пароль", "email", "existing", "wrong", "rejected",
    ),
    AuthCase("AUTH-07", "Телефон отклонён в поле email", "phone", "existing", "correct", "rejected"),
    AuthCase("AUTH-08", "Подсказка о неверном формате email", "email", "invalid_email", "sample", "email_format"),
]

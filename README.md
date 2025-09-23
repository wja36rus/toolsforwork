# Набор утилит для работы

## Функциональность

### Enum updater

- Преобразует `enum` в `const object as const`
- Создает тип `TEnumName = typeof EnumName[keyof typeof EnumName]`
- Сохраняет комментарии и оригинальные значения
- Поддерживает числовые, строковые и автоинкрементные значения

#### Использование

1. Откройте TypeScript файл (.ts или .tsx)
2. Вызовите команду одним из способов:
   - `Ctrl+Shift+P` → "Преобразовать Enum в Object с типом"
   - Правый клик в редакторе → "Преобразовать Enum в Object с типом"

#### Пример преобразования

**До:**

```typescript
enum Status {
  Active = 1,
  Inactive = 2,
  Pending = 3,
}
```

**После:**

```typescript
const Status = {
  Active: 1,
  Inactive: 2,
  Pending: 3,
} as const;

export type TStatus = (typeof Status)[keyof typeof Status];
```

# Требования

- Python 3.x должен быть установлен и доступен в PATH
- TypeScript файлы

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
   - Горячая клавиша по умолчанию `shift+d`

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

### mport updater

- Преобразует импорты в файле соголасно контекста использования
- Если используется как тип, проставляет в импорте type

#### Использование

1. Откройте TypeScript файл (.ts или .tsx)
2. Вызовите команду одним из способов:
   - `Ctrl+Shift+P` → "Преобразовать импорты"
   - Правый клик в редакторе → "Преобразовать импорты"
   - Горячая клавиша по умолчанию `shift+i`

#### Пример преобразования

**До:**

```typescript
import { ReactNode } from "react";
import {
  EMultiobjectDomainType,
  TypeProperty,
  VisualMode,
  TVisualMode,
} from "@ggis/utils";

import { EWindowType } from "../../../shared/constants";
import { TAttribute } from "../../../shared/types";

const visual = VisualMode.Default;
export interface IDataAttributes {
  id?: number;
  label?: string;
  typeProperty?: TypeProperty;
  drawerMode?: TVisualMode;
  value?: string;
  domainRole?: EMultiobjectDomainType;
  keys?: string[];
  visible?: boolean;
}

export interface IPropsAttributeComponent {
  data: IDataAttributes;
  deleteBtn?: ReactNode | null;
  disabled?: boolean;
  isDrawingStyleSolid?: boolean;
  attributesCard?: TAttribute;
  setWindow?: (open: EWindowType) => void;
  setIntervalOrder?: (id: number) => void;
  onChange?: (e: string, key?: string) => void;
  isShort?: boolean;

  hideArrow?: null;
}
```

**После:**

```typescript
import type { ReactNode } from "react";

import {
  VisualMode,
  type EMultiobjectDomainType,
  type TVisualMode,
  type TypeProperty,
} from "@ggis/utils";

import type { EWindowType } from "../../../shared/constants";
import type { TAttribute } from "../../../shared/types";

const visual = VisualMode.Default;
export interface IDataAttributes {
  id?: number;
  label?: string;
  typeProperty?: TypeProperty;
  drawerMode?: TVisualMode;
  value?: string;
  domainRole?: EMultiobjectDomainType;
  keys?: string[];
  visible?: boolean;
}

export interface IPropsAttributeComponent {
  data: IDataAttributes;
  deleteBtn?: ReactNode | null;
  disabled?: boolean;
  isDrawingStyleSolid?: boolean;
  attributesCard?: TAttribute;
  setWindow?: (open: EWindowType) => void;
  setIntervalOrder?: (id: number) => void;
  onChange?: (e: string, key?: string) => void;
  isShort?: boolean;

  hideArrow?: null;
}
```

# Требования

- Python 3.x должен быть установлен и доступен в PATH
- TypeScript файлы

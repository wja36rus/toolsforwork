import re
import sys
import os
import codecs

def setup_encoding():
    """Настраивает кодировку для корректного вывода Unicode символов"""
    if sys.stdout.encoding is None or sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        except:
            pass

def parse_enum_values(enum_body):
    """Парсит значения из тела enum с сохранением оригинальных значений"""
    values = []
    lines = enum_body.strip().split('\n')
    
    for line in lines:
        original_line = line.strip()
        if original_line and not original_line.startswith('//') and not original_line.startswith('/*'):
            # Сохраняем оригинальную строку для анализа
            line = original_line
            
            # Удаляем комментарии в конце строки для парсинга, но сохраняем оригинал
            clean_line = re.sub(r'//.*$', '', line).strip()
            clean_line = re.sub(r'/\*.*\*/', '', clean_line).strip()
            
            if clean_line and not clean_line.startswith('}'):
                # Обрабатываем строки вида Key = Value или просто Key
                if '=' in clean_line:
                    key_value = clean_line.split('=', 1)
                    key = key_value[0].strip()
                    value = key_value[1].strip()
                    # Удаляем запятую если есть
                    key = key.rstrip(',')
                    value = value.rstrip(',')
                    
                    # Определяем тип значения
                    if value.isdigit():
                        # Числовое значение
                        values.append({
                            'key': key,
                            'value': int(value),
                            'type': 'number',
                            'original_line': original_line
                        })
                    elif value.startswith("'") and value.endswith("'") or value.startswith('"') and value.endswith('"'):
                        # Строковое значение в кавычках
                        str_value = value[1:-1]
                        values.append({
                            'key': key,
                            'value': str_value,
                            'type': 'string',
                            'original_line': original_line
                        })
                    else:
                        # Идентификатор или другое значение
                        values.append({
                            'key': key,
                            'value': value,
                            'type': 'identifier',
                            'original_line': original_line
                        })
                else:
                    # Если нет =, то это просто ключ (автоинкремент)
                    key = clean_line.rstrip(',')
                    values.append({
                        'key': key,
                        'value': None,  # Будет определено позже
                        'type': 'auto',
                        'original_line': original_line
                    })
    
    # Обрабатываем автоинкрементные значения
    current_number = 0
    for item in values:
        if item['type'] == 'auto' and item['value'] is None:
            item['value'] = current_number
            item['type'] = 'number'
            current_number += 1
        elif item['type'] == 'auto' and isinstance(item['value'], int):
            current_number = item['value'] + 1
        elif item['type'] == 'number':
            current_number = item['value'] + 1
    
    return values

def create_const_object(enum_name, values):
    """Создает const object из значений enum с сохранением оригинальных значений и комментариев"""
    const_lines = [f"export const {enum_name} = {{"]
    
    for item in values:
        key = item['key']
        value = item['value']
        original_line = item['original_line']
        
        # Сохраняем комментарии из оригинальной строки
        comment_match = re.search(r'(\s*//.*$|\s*/\*.*\*/)', original_line)
        comment = comment_match.group(0) if comment_match else ""
        
        if item['type'] == 'number':
            const_lines.append(f"  {key}: {value},{comment}")
        else:
            const_lines.append(f"  {key}: '{value}',{comment}")
    
    const_lines.append("} as const;")
    return '\n'.join(const_lines)

def create_type_definition(enum_name):
    """Создает тип в формате keyof typeof EnumName[keyof typeof EnumName]"""
    type_name = f"T{enum_name}"
    return f"export type {type_name} = typeof {enum_name}[keyof typeof {enum_name}];"

def transform_enum_to_const_object(file_path):
    """Основная функция преобразования"""
    try:
        # Чтение файла
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Регулярное выражение для поиска enum
        enum_regex = r'(?:(?:export\s+)?(?:declare\s+)?(?:const\s+)?|(?:declare\s+)?(?:export\s+)?(?:const\s+)?|(?:const\s+)?(?:export\s+)?(?:declare\s+)?)enum\s+(\w+)\s*\{([^}]+)\}'        
        
        replacements = []
        transformed_content = content
        
        # Поиск всех enum в файле
        for match in re.finditer(enum_regex, content, re.DOTALL):
            enum_name = match.group(1)
            enum_body = match.group(2)
            
            # Парсинг значений enum
            values = parse_enum_values(enum_body)
            
            if not values:
                print(f"[WARNING] Не удалось извлечь значения из enum {enum_name}")
                continue
            
            # Создание const объекта
            const_object = create_const_object(enum_name, values)
            
            # Создание типа в новом формате
            type_definition = create_type_definition(enum_name)
            
            # Замена в содержании
            transformed_content = transformed_content.replace(match.group(0), const_object + '\n\n' + type_definition)
            
            replacements.append({
                'enum_name': enum_name,
                'type_name': f"T{enum_name}",
                'values': values
            })
        
        if not replacements:
            print("[ERROR] Enum'ы не найдены в файле")
            return
        
        # Запись измененного файла (перезаписываем исходный)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(transformed_content)
        
        # Вывод информации (без эмодзи для совместимости)
        print(f"[SUCCESS] Файл успешно преобразован: {file_path}")
        print("\nПреобразованные enum'ы:")
        for replacement in replacements:
            print(f"  - {replacement['enum_name']} -> {replacement['type_name']}")
            value_list = []
            for item in replacement['values']:
                if item['type'] == 'number':
                    value_list.append(f"{item['key']}={item['value']}")
                else:
                    value_list.append(f"{item['key']}='{item['value']}'")
            print(f"    Значения: {', '.join(value_list)}")
            print()
        
    except FileNotFoundError:
        print(f"[ERROR] Файл не найден: {file_path}")
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")

def optimize_imports(file_path):
    """Оптимизирует импорты, добавляя type где необходимо"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Регулярное выражение для поиска импортов
        import_pattern = r'import\s+\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"];'
        
        # Собираем информацию об использовании идентификаторов
        type_usage = {}
        value_usage = {}
        
        # Ищем типы в различных контекстах
        type_patterns = [
            r'[:?]\s*(\b[T]?[A-Z][a-zA-Z]+\b)[,\s;)\]]',  # аннотации типов
            r'\bin\s+(\b[T]?[A-Z][a-zA-Z]+\b)\b',         # выражения "in Type"
            r'\[\s*\w+\s+in\s+(\b[T]?[A-Z][a-zA-Z]+\b)\s*\]',  # [key in Type]
            r'<\s*(\b[T]?[A-Z][a-zA-Z]+\b)[^>]*>',        # дженерики <TType>
            r'\btype\s+\w+\s*=\s*(\b[T]?[A-Z][a-zA-Z]+\b)\b',  # type Alias = TType
            r'\bRecord\s*<\s*(\b[T]?[A-Z][a-zA-Z]+\b)[^>]*>',  # Record<TType, ...>
            r'\bArray\s*<\s*(\b[T]?[A-Z][a-zA-Z]+\b)[^>]*>',   # Array<TType>
            r'\bPromise\s*<\s*(\b[T]?[A-Z][a-zA-Z]+\b)[^>]*>', # Promise<TType>
            r'\bMap\s*<\s*(\b[T]?[A-Z][a-zA-Z]+\b)[^>]*>',     # Map<TType>
            r'\bSet\s*<\s*(\b[T]?[A-Z][a-zA-Z]+\b)[^>]*>',     # Set<TType>
            r'\bas\s+(\b[T]?[A-Z][a-zA-Z]+\b)\b',              # as Type (приведение типов)
            r'\bexport\s+type\s+\w+\s*=\s*(\b[T]?[A-Z][a-zA-Z]+\b)\b',  # export type TWindow = TType
            r'\bexport\s+interface\s+\w+\s*extends\s*(\b[T]?[A-Z][a-zA-Z]+\b)\b',  # export interface extends TType
            r'\bexport\s+\w+\s*:\s*(\b[T]?[A-Z][a-zA-Z]+\b)\b',  # export variable: TType
        ]
        
        for pattern in type_patterns:
            for match in re.finditer(pattern, content):
                type_name = match.group(1)
                if type_name:  # Проверяем, что группа захватила значение
                    type_usage[type_name] = True
        
        # Ищем значения (использование через точку, например SomeEnum.Value)
        value_pattern = r'\b([A-Z][a-zA-Z]+)\.\w+'
        for match in re.finditer(value_pattern, content):
            value_name = match.group(1)
            value_usage[value_name] = True
        
        # Также ищем использование как значений (без точки)
        value_usage_patterns = [
            r'\b([A-Z][a-zA-Z]+)\s*\.',        # SomeEnum.
            r'=\s*([A-Z][a-zA-Z]+)\b',         # = SomeEnum
            r'\b([A-Z][a-zA-Z]+)\[',           # SomeEnum[
            r'\[\s*([A-Z][a-zA-Z]+)\s*\]',     # [SomeEnum]
            r'new\s+([A-Z][a-zA-Z]+)\b',       # new SomeEnum
            r'\binstanceof\s+([A-Z][a-zA-Z]+)\b', # instanceof SomeEnum
            r'\btypeof\s+([A-Z][a-zA-Z]+)\b',  # typeof SomeEnum
            r'\bexport\s+default\s+([A-Z][a-zA-Z]+)\b',  # export default SomeEnum
            r'\bexport\s+\{\s*([A-Z][a-zA-Z]+)\s*\}',    # export { SomeEnum }
            r'\bexport\s+const\s+\w+\s*=\s*([A-Z][a-zA-Z]+)\b',  # export const x = SomeEnum
            r'\bexport\s+function\s+\w+\s*\(\w+\s*:\s*([A-Z][a-zA-Z]+)\b',  # export function(x: SomeEnum)
        ]
        
        for pattern in value_usage_patterns:
            for match in re.finditer(pattern, content):
                for i in range(1, 4):  # Проверяем все группы захвата
                    value_name = match.group(i)
                    if value_name:  # Проверяем, что группа захватила значение
                        value_usage[value_name] = True
                        break
        
        # Обрабатываем каждый импорт
        def replace_import(match):
            import_body = match.group(1)
            module_path = match.group(2)
            
            # Разбираем импортируемые элементы
            items = [item.strip() for item in import_body.split(',') if item.strip()]
            
            # Определяем, какие элементы используются как типы, а какие как значения
            type_items = []
            value_items = []
            
            for item in items:
                # Проверяем использование как типа
                is_type = item in type_usage
                # Проверяем использование как значения
                is_value = item in value_usage
                
                if is_type and not is_value:
                    type_items.append(item)
                elif is_value and not is_type:
                    value_items.append(item)
                else:
                    # Если используется и как тип и как значение, или использование не определено
                    # оставляем как есть (без type)
                    value_items.append(item)
            
            # Собираем новый импорт
            new_import_parts = []
            
            # Сначала значения
            if value_items:
                new_import_parts.append(', '.join(value_items))
            
            # Затем типы с ключевым словом type
            if type_items:
                if new_import_parts:
                    # Если уже есть значения, добавляем типы с префиксом "type"
                    new_import_parts.append('type ' + ', type '.join(type_items))
                else:
                    # Если только типы, используем import type
                    new_import_parts.append(', '.join(type_items))
            
            if not new_import_parts:
                return match.group(0)
            
            new_import_body = ', '.join(new_import_parts)
            
            # Если все элементы - типы, используем import type
            if not value_items and type_items:
                return f'import type {{{new_import_body}}} from \"{module_path}\";'
            else:
                return f'import {{{new_import_body}}} from \"{module_path}\";'
        
        # Заменяем импорты
        new_content = re.sub(import_pattern, replace_import, content)
        
        # Записываем изменения
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(f"[SUCCESS] Импорты оптимизированы: {file_path}")
        
        # Отладочная информация
        print("\nОтладочная информация:")
        print("Типы:", sorted(type_usage.keys()))
        print("Значения:", sorted(value_usage.keys()))
        
        # Детальная информация по каждому импорту
        print("\nДетальный анализ импортов:")
        for match in re.finditer(import_pattern, content):
            import_body = match.group(1)
            module_path = match.group(2)
            items = [item.strip() for item in import_body.split(',') if item.strip()]
            
            print(f"Импорт из '{module_path}':")
            for item in items:
                is_type = item in type_usage
                is_value = item in value_usage
                usage_type = "тип" if is_type and not is_value else "значение" if is_value and not is_type else "оба" if is_type and is_value else "не определено"
                print(f"  {item}: {usage_type}")
        
    except Exception as e:
        print(f"[ERROR] Ошибка при оптимизации импортов: {e}")

def main():
    """Основная функция"""
    # Настраиваем кодировку
    setup_encoding()
    
    if len(sys.argv) != 2:
        print("Использование: python enum_updater.py <path_to_ts_file>")
        print("Пример: python enum_updater.py example.ts")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"[ERROR] Файл не существует: {file_path}")
        sys.exit(1)
    
    if not file_path.endswith(('.ts', '.tsx')):
        print("[WARNING] Файл может не быть TypeScript файлом")
    
    # Сначала преобразуем enum
    transform_enum_to_const_object(file_path)
    
    # Затем оптимизируем импорты
    optimize_imports(file_path)

if __name__ == "__main__":
    main()
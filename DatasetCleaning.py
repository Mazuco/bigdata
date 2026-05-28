import re
import csv
import json

# Sample raw data — messy, as it comes from the real world
raw_records = [
    {'name': '  mary silva  ',  'salary': 'R$ 4.500,00', 'email': 'mary@email.com',  'phone': '(11) 91234-5678'},
    {'name': 'JOHN DOE',        'salary': 'R$ 12.300,50','email': 'JOHN@EMAIL.COM',   'phone': '11987654321'},
    {'name': 'Anna  Jones',     'salary': '3200,00',      'email': 'anna@company',     'phone': '(21)99876-5432'},
    {'name': '  CARLOS LIMA  ', 'salary': 'R$ 7.800,75', 'email': 'carlos@corp.org',  'phone': '(31) 98765-4321'},
]

def clean_name(raw):
    return raw.strip().title()

def clean_salary(raw):
    cleaned = raw.replace('R$', '').replace('.', '').replace(',', '.').strip()
    try:
        return round(float(cleaned), 2)
    except ValueError:
        return None

def clean_email(raw):
    return raw.strip().lower()

def clean_phone(raw):
    # Keep only digits
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 11:
        return f'({digits[:2]}) {digits[2:7]}-{digits[7:]}'
    return None

def validate_email(email):
    pattern = r'^[\w.-]+@[\w.-]+\.\w{2,}$'
    return bool(re.match(pattern, email))

# Process all records
cleaned_records = []
issues = []

for record in raw_records:
    name   = clean_name(record['name'])
    salary = clean_salary(record['salary'])
    email  = clean_email(record['email'])
    phone  = clean_phone(record['phone'])

    record_issues = []
    if salary is None:
        record_issues.append('invalid salary')
    if not validate_email(email):
        record_issues.append('invalid email')
    if phone is None:
        record_issues.append('invalid phone')

    cleaned = {
        'name'  : name,
        'salary': salary,
        'email' : email,
        'phone' : phone,
        'valid' : len(record_issues) == 0
    }
    cleaned_records.append(cleaned)

    if record_issues:
        issues.append({'name': name, 'issues': record_issues})

# Show results
print(f'{"Name":<20} {"Salary":>12}  {"Email":<25} {"Phone":<18} {"Valid"}')
print('-' * 85)
for r in cleaned_records:
    salary_str = f'R$ {r["salary"]:,.2f}' if r['salary'] else 'N/A'
    phone_str  = r['phone'] or 'N/A'
    valid_str  = '✓' if r['valid'] else '✗'
    print(f'{r["name"]:<20} {salary_str:>12}  {r["email"]:<25} {phone_str:<18} {valid_str}')

print(f'\nRecords with issues:')
for issue in issues:
    print(f'  {issue["name"]}: {", ".join(issue["issues"])}')


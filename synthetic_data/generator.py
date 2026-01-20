"""
Módulo para generar datos sintéticos.
"""
from faker import Faker
import random


class SyntheticDataGenerator:
    """Genera datos sintéticos basados en perfiles y esquemas."""
    
    def __init__(self, locale='es_ES', seed=None):
        """
        Inicializa el generador.
        
        Args:
            locale: Localización para los datos generados
            seed: Semilla para reproducibilidad
        """
        self.faker = Faker(locale)
        if seed:
            Faker.seed(seed)
            random.seed(seed)
    
    def generate_person(self, count=1):
        """
        Genera datos de personas.
        
        Args:
            count: Número de personas a generar
            
        Returns:
            list: Lista de diccionarios con datos de personas
        """
        persons = []
        for _ in range(count):
            person = {
                'id': self.faker.uuid4(),
                'name': self.faker.name(),
                'email': self.faker.email(),
                'phone': self.faker.phone_number(),
                'address': self.faker.address(),
                'birthdate': self.faker.date_of_birth().isoformat(),
                'ssn': self.faker.ssn(),
            }
            persons.append(person)
        return persons
    
    def generate_company(self, count=1):
        """
        Genera datos de empresas.
        
        Args:
            count: Número de empresas a generar
            
        Returns:
            list: Lista de diccionarios con datos de empresas
        """
        companies = []
        for _ in range(count):
            company = {
                'id': self.faker.uuid4(),
                'name': self.faker.company(),
                'email': self.faker.company_email(),
                'phone': self.faker.phone_number(),
                'address': self.faker.address(),
                'tax_id': self.faker.bothify(text='??-#######'),
            }
            companies.append(company)
        return companies
    
    def generate_transaction(self, count=1):
        """
        Genera datos de transacciones.
        
        Args:
            count: Número de transacciones a generar
            
        Returns:
            list: Lista de diccionarios con datos de transacciones
        """
        transactions = []
        for _ in range(count):
            transaction = {
                'id': self.faker.uuid4(),
                'date': self.faker.date_time_this_year().isoformat(),
                'amount': round(random.uniform(10, 10000), 2),
                'currency': self.faker.currency_code(),
                'description': self.faker.sentence(),
                'card_number': self.faker.credit_card_number(),
            }
            transactions.append(transaction)
        return transactions
    
    def generate_from_schema(self, schema, count=1):
        """
        Genera datos basados en un esquema personalizado.
        
        Args:
            schema: Diccionario con el esquema de datos
            count: Número de registros a generar
            
        Returns:
            list: Lista de diccionarios con datos generados
        """
        records = []
        for _ in range(count):
            record = {}
            for field, field_type in schema.items():
                generator = getattr(self.faker, field_type, None)
                if generator:
                    record[field] = generator()
                else:
                    record[field] = None
            records.append(record)
        return records

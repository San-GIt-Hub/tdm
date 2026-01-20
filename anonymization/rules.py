"""
Módulo para definir y aplicar reglas de anonimización.
"""


class AnonymizationRule:
    """Representa una regla de anonimización."""
    
    def __init__(self, field_name, data_type, method, **kwargs):
        """
        Inicializa una regla de anonimización.
        
        Args:
            field_name: Nombre del campo a anonimizar
            data_type: Tipo de dato (email, phone, name, etc.)
            method: Método de anonimización (mask, hash, pseudonymize, etc.)
            **kwargs: Argumentos adicionales para el método
        """
        self.field_name = field_name
        self.data_type = data_type
        self.method = method
        self.params = kwargs
    
    def __repr__(self):
        return f"AnonymizationRule(field='{self.field_name}', method='{self.method}')"


class RuleEngine:
    """Motor para gestionar y aplicar reglas de anonimización."""
    
    def __init__(self):
        self.rules = []
    
    def add_rule(self, rule):
        """
        Añade una regla al motor.
        
        Args:
            rule: Regla de anonimización
        """
        self.rules.append(rule)
    
    def remove_rule(self, field_name):
        """
        Elimina una regla por nombre de campo.
        
        Args:
            field_name: Nombre del campo
        """
        self.rules = [r for r in self.rules if r.field_name != field_name]
    
    def get_rule(self, field_name):
        """
        Obtiene la regla para un campo específico.
        
        Args:
            field_name: Nombre del campo
            
        Returns:
            AnonymizationRule: Regla encontrada o None
        """
        for rule in self.rules:
            if rule.field_name == field_name:
                return rule
        return None
    
    def apply_rules(self, data, anonymizer):
        """
        Aplica todas las reglas a un conjunto de datos.
        
        Args:
            data: Diccionario con los datos a anonimizar
            anonymizer: Instancia de DataAnonymizer
            
        Returns:
            dict: Datos anonimizados
        """
        anonymized_data = data.copy()
        
        for rule in self.rules:
            if rule.field_name in anonymized_data:
                value = anonymized_data[rule.field_name]
                method = getattr(anonymizer, rule.method)
                
                # Pasar data_type como parámetro para métodos que lo necesiten
                if rule.method == 'pseudonymize':
                    anonymized_data[rule.field_name] = method(value, data_type=rule.data_type)
                else:
                    anonymized_data[rule.field_name] = method(value, **rule.params)
        
        return anonymized_data

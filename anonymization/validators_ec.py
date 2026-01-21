"""
Validadores específicos para Ecuador (Cédula y RUC).
"""


class EcuadorValidators:
    """Validadores de identificación ecuatorianos."""
    
    @staticmethod
    def validar_cedula(cedula):
        """
        Valida una cédula ecuatoriana usando el algoritmo módulo 10.
        
        Args:
            cedula: String de 10 dígitos
            
        Returns:
            bool: True si la cédula es válida
        """
        if not cedula or len(str(cedula)) != 10:
            return False
        
        try:
            cedula = str(cedula)
            if not cedula.isdigit():
                return False
            
            # Los dos primeros dígitos deben ser entre 01 y 24
            provincia = int(cedula[0:2])
            if provincia < 1 or provincia > 24:
                return False
            
            # Algoritmo módulo 10
            coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
            suma = 0
            
            for i in range(9):
                valor = int(cedula[i]) * coeficientes[i]
                if valor >= 10:
                    valor -= 9
                suma += valor
            
            digito_verificador = int(cedula[9])
            residuo = suma % 10
            resultado = 0 if residuo == 0 else 10 - residuo
            
            return resultado == digito_verificador
            
        except (ValueError, IndexError):
            return False
    
    @staticmethod
    def validar_ruc_natural(ruc):
        """
        Valida un RUC de persona natural (cédula + 001).
        
        Args:
            ruc: String de 13 dígitos
            
        Returns:
            bool: True si el RUC es válido
        """
        if not ruc or len(str(ruc)) != 13:
            return False
        
        try:
            ruc = str(ruc)
            if not ruc.isdigit():
                return False
            
            # Debe terminar en 001
            if ruc[10:13] != '001':
                return False
            
            # Los primeros 10 dígitos deben ser una cédula válida
            cedula = ruc[0:10]
            return EcuadorValidators.validar_cedula(cedula)
            
        except (ValueError, IndexError):
            return False
    
    @staticmethod
    def validar_ruc_empresa(ruc):
        """
        Valida un RUC de empresa (tercer dígito debe ser 9).
        
        Args:
            ruc: String de 13 dígitos
            
        Returns:
            bool: True si el RUC es válido
        """
        if not ruc or len(str(ruc)) != 13:
            return False
        
        try:
            ruc = str(ruc)
            if not ruc.isdigit():
                return False
            
            # Tercer dígito debe ser 9
            if ruc[2] != '9':
                return False
            
            # Los dos primeros dígitos deben ser entre 01 y 24
            provincia = int(ruc[0:2])
            if provincia < 1 or provincia > 24:
                return False
            
            # Debe terminar en 001
            if ruc[10:13] != '001':
                return False
            
            # Algoritmo módulo 11 (sobre 9 dígitos: 2 provincia + 1 tipo + 6 secuencial)
            coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
            suma = 0
            
            for i in range(9):
                suma += int(ruc[i]) * coeficientes[i]
            
            digito_verificador = int(ruc[9])
            residuo = suma % 11
            resultado = 0 if residuo == 0 else 11 - residuo
            
            return resultado == digito_verificador
            
        except (ValueError, IndexError):
            return False
    
    @staticmethod
    def generar_cedula_valida(provincia=17, random_gen=None):
        """
        Genera una cédula ecuatoriana válida.
        
        Args:
            provincia: Código de provincia (01-24)
            random_gen: Generador random para determinismo
            
        Returns:
            str: Cédula válida de 10 dígitos
        """
        import random
        if random_gen is None:
            random_gen = random
        
        # Asegurar que la provincia esté en rango válido
        if provincia < 1 or provincia > 24:
            provincia = 17  # Pichincha por defecto
        
        # Generar 8 dígitos aleatorios
        cedula_base = f"{provincia:02d}"
        for _ in range(7):
            cedula_base += str(random_gen.randint(0, 9))
        
        # Calcular dígito verificador
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0
        
        for i in range(9):
            valor = int(cedula_base[i]) * coeficientes[i]
            if valor >= 10:
                valor -= 9
            suma += valor
        
        residuo = suma % 10
        digito_verificador = 0 if residuo == 0 else 10 - residuo
        
        return cedula_base + str(digito_verificador)
    
    @staticmethod
    def generar_ruc_natural(provincia=17, random_gen=None):
        """
        Genera un RUC de persona natural válido.
        
        Args:
            provincia: Código de provincia (01-24)
            random_gen: Generador random para determinismo
            
        Returns:
            str: RUC válido de 13 dígitos
        """
        cedula = EcuadorValidators.generar_cedula_valida(provincia, random_gen)
        return cedula + "001"
    
    @staticmethod
    def generar_ruc_empresa(provincia=17, random_gen=None):
        """
        Genera un RUC de empresa válido.
        
        Args:
            provincia: Código de provincia (01-24)
            random_gen: Generador random para determinismo
            
        Returns:
            str: RUC de empresa válido de 13 dígitos
        """
        import random
        if random_gen is None:
            random_gen = random
        
        # Asegurar que la provincia esté en rango válido
        if provincia < 1 or provincia > 24:
            provincia = 17  # Pichincha por defecto
        
        # Formato RUC Empresa: PP 9 XXXXXX V 001
        # PP = Provincia (2 dígitos)
        # 9 = Tipo empresa (1 dígito)
        # XXXXXX = Secuencial (6 dígitos)
        # V = Verificador (1 dígito)
        # 001 = Establecimiento (3 dígitos)
        # Total: 2 + 1 + 6 + 1 + 3 = 13 dígitos
        
        ruc_base = f"{provincia:02d}9"
        for _ in range(6):
            ruc_base += str(random_gen.randint(0, 9))
        
        # Calcular dígito verificador con módulo 11 (sobre 9 dígitos: 2+1+6)
        coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
        suma = 0
        
        for i in range(9):
            suma += int(ruc_base[i]) * coeficientes[i]
        
        residuo = suma % 11
        digito_verificador = 0 if residuo == 0 else 11 - residuo
        
        return ruc_base + str(digito_verificador) + "001"

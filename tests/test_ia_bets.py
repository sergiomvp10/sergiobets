import unittest
from ia_bets import (
    es_liga_conocida, calcular_probabilidades, analizar_partido,
    generar_prediccion, filtrar_apuestas_inteligentes, simular_datos_prueba
)

class TestIABets(unittest.TestCase):
    
    def setUp(self):
        self.partido_ejemplo = {
            "hora": "15:00",
            "liga": "Premier League",
            "local": "Manchester City",
            "visitante": "Arsenal",
            "cuotas": {
                "casa": "Bet365",
                "local": "1.65",
                "empate": "3.80",
                "visitante": "4.20"
            }
        }
        
        self.partido_liga_desconocida = {
            "hora": "15:00",
            "liga": "Liga Desconocida XYZ",
            "local": "Equipo A",
            "visitante": "Equipo B",
            "cuotas": {
                "casa": "Bet365",
                "local": "1.65",
                "empate": "3.80",
                "visitante": "4.20"
            }
        }
        
        self.partido_cuota_alta = {
            "hora": "15:00",
            "liga": "Premier League",
            "local": "Manchester City",
            "visitante": "Arsenal",
            "cuotas": {
                "casa": "Bet365",
                "local": "2.50",
                "empate": "3.80",
                "visitante": "4.20"
            }
        }

    def test_es_liga_conocida(self):
        self.assertTrue(es_liga_conocida("Premier League"))
        self.assertTrue(es_liga_conocida("La Liga"))
        self.assertTrue(es_liga_conocida("Serie A"))
        self.assertFalse(es_liga_conocida("Liga Desconocida XYZ"))

    def test_calcular_probabilidades(self):
        cuotas = {"local": "2.00", "empate": "3.00", "visitante": "4.00"}
        probabilidades = calcular_probabilidades(cuotas)
        
        self.assertIn("local", probabilidades)
        self.assertIn("empate", probabilidades)
        self.assertIn("visitante", probabilidades)
        
        total = sum(probabilidades.values())
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_calcular_probabilidades_cuotas_invalidas(self):
        cuotas = {"local": "invalid", "empate": "3.00", "visitante": "4.00"}
        probabilidades = calcular_probabilidades(cuotas)
        
        total = sum(probabilidades.values())
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_analizar_partido(self):
        analisis = analizar_partido(self.partido_ejemplo)
        
        self.assertIn("partido", analisis)
        self.assertIn("liga", analisis)
        self.assertIn("prediccion", analisis)
        self.assertIn("cuota", analisis)
        self.assertIn("confianza", analisis)
        self.assertIn("valor_esperado", analisis)
        
        self.assertEqual(analisis["liga"], "Premier League")
        self.assertIsInstance(analisis["cuota"], float)
        self.assertIsInstance(analisis["confianza"], float)

    def test_generar_prediccion_valida(self):
        partido_valido = {
            "hora": "15:00",
            "liga": "Premier League",
            "local": "Manchester City",
            "visitante": "Arsenal",
            "cuotas": {
                "casa": "Bet365",
                "local": "1.70",  # Higher odds within range 1.50-1.75
                "empate": "5.00",
                "visitante": "6.00"
            }
        }
        
        prediccion = generar_prediccion(partido_valido)
        
        self.assertIsNotNone(prediccion)
        self.assertIn("partido", prediccion)
        self.assertIn("prediccion", prediccion)
        self.assertIn("cuota", prediccion)
        self.assertIn("stake_recomendado", prediccion)
        self.assertIn("confianza", prediccion)

    def test_generar_prediccion_liga_desconocida(self):
        prediccion = generar_prediccion(self.partido_liga_desconocida)
        self.assertIsNone(prediccion)

    def test_generar_prediccion_cuota_alta(self):
        prediccion = generar_prediccion(self.partido_cuota_alta)
        self.assertIsNone(prediccion)

    def test_filtrar_apuestas_inteligentes(self):
        partidos = [
            self.partido_ejemplo,
            self.partido_liga_desconocida,
            self.partido_cuota_alta
        ]
        
        predicciones = filtrar_apuestas_inteligentes(partidos)
        
        self.assertIsInstance(predicciones, list)
        self.assertLessEqual(len(predicciones), 5)
        
        for prediccion in predicciones:
            self.assertIn("partido", prediccion)
            self.assertIn("cuota", prediccion)
            self.assertTrue(1.50 <= prediccion["cuota"] <= 1.75)

    def test_simular_datos_prueba(self):
        datos = simular_datos_prueba()
        
        self.assertIsInstance(datos, list)
        self.assertGreater(len(datos), 0)
        
        for partido in datos:
            self.assertIn("hora", partido)
            self.assertIn("liga", partido)
            self.assertIn("local", partido)
            self.assertIn("visitante", partido)
            self.assertIn("cuotas", partido)

if __name__ == '__main__':
    unittest.main()

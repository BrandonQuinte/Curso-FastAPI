# monitoring/alerts.py
from typing import Dict, List, Callable
from dataclasses import dataclass
import time
import logging
import smtplib
from email.mime.text import MIMEText


@dataclass
class AlertRule:
    name: str
    metric_name: str
    threshold: float
    comparison: str  # 'gt', 'lt', 'eq'
    duration: int  # segundos
    action: Callable


class AlertManager:
    def __init__(self, domain: str = "lang"):
        self.domain = domain
        self.rules: List[AlertRule] = []
        self.alert_state: Dict[str, Dict] = {}

    def add_rule(self, rule: AlertRule):
        """Añade una regla de alerta"""
        self.rules.append(rule)
        self.alert_state[rule.name] = {
            "triggered": False,
            "last_check": 0,
            "trigger_count": 0
        }

    def check_alerts(self, metrics_data: Dict[str, float]):
        """Verifica todas las reglas de alerta"""
        current_time = time.time()

        for rule in self.rules:
            if rule.metric_name in metrics_data:
                value = metrics_data[rule.metric_name]
                should_trigger = self._evaluate_rule(rule, value)

                if should_trigger:
                    self._handle_alert(rule, value, current_time)
                else:
                    self._reset_alert(rule.name)

    def _evaluate_rule(self, rule: AlertRule, value: float) -> bool:
        """Evalúa si una regla debe disparar alerta"""
        if rule.comparison == "gt":
            return value > rule.threshold
        elif rule.comparison == "lt":
            return value < rule.threshold
        elif rule.comparison == "eq":
            return value == rule.threshold
        return False

    def _handle_alert(self, rule: AlertRule, value: float, current_time: float):
        """Maneja el disparo de una alerta"""
        state = self.alert_state[rule.name]

        if not state["triggered"]:
            state["triggered"] = True
            state["trigger_time"] = current_time

        # Verificar duración sostenida
        if current_time - state.get("trigger_time", 0) >= rule.duration:
            rule.action(rule, value)
            state["trigger_count"] += 1

    def _reset_alert(self, rule_name: str):
        """Resetea el estado de una alerta"""
        if rule_name in self.alert_state:
            self.alert_state[rule_name]["triggered"] = False



# Acciones de alerta 

def email_alert(rule: AlertRule, value: float):
    """Envía alerta por email (placeholder)"""
    # Aquí puedes configurar un servidor SMTP real
    print(f"📧 Email ALERT: {rule.name} - Valor: {value} (Umbral: {rule.threshold})")


def log_alert(rule: AlertRule, value: float):
    """Registra alerta en logs"""
    logging.warning(f"🚨 ALERTA: {rule.name} - Valor: {value} (Umbral: {rule.threshold})")

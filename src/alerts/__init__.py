# src/alerts/__init__.py
"""
Módulo de Alertas y Notificaciones
Sistema de monitoreo automático para el sistema de gestión
"""

from .notification_system import AlertsManager, AlertsWindow, abrir_centro_alertas

__all__ = ['AlertsManager', 'AlertsWindow', 'abrir_centro_alertas']
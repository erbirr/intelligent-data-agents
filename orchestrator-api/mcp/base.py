# mcp/base.py - Clases base para implementar MCP
import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class MCPMessageType(Enum):
    """Tipos de mensajes en el protocolo MCP"""
    REQUEST = "request"
    RESPONSE = "response" 
    NOTIFICATION = "notification"

@dataclass
class MCPMessage:
    """Mensaje básico del protocolo MCP"""
    id: str
    type: MCPMessageType
    method: str
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class MCPServer(ABC):
    """
    Clase base para servidores MCP.
    Un servidor MCP expone recursos y herramientas que otros pueden usar.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.resources = {}  # Recursos que este servidor expone
        self.tools = {}      # Herramientas que este servidor provee
        self.initialized = False
    
    @abstractmethod
    async def initialize(self):
        """Inicializa el servidor MCP"""
        pass
    
    @abstractmethod
    async def handle_request(self, message: MCPMessage) -> MCPMessage:
        """Maneja una petición MCP y retorna una respuesta"""
        pass
    
    def register_resource(self, name: str, resource: Any):
        """Registra un recurso que este servidor puede proveer"""
        self.resources[name] = resource
        logger.info(f"Recurso '{name}' registrado en servidor {self.name}")
    
    def register_tool(self, name: str, tool_func: callable, description: str):
        """Registra una herramienta que este servidor puede ejecutar"""
        self.tools[name] = {
            "function": tool_func,
            "description": description
        }
        logger.info(f"Herramienta '{name}' registrada en servidor {self.name}")
    
    async def get_resources(self) -> Dict[str, Any]:
        """Retorna todos los recursos disponibles"""
        return {
            "resources": list(self.resources.keys()),
            "server": self.name
        }
    
    async def get_tools(self) -> Dict[str, Any]:
        """Retorna todas las herramientas disponibles"""
        return {
            "tools": {name: info["description"] for name, info in self.tools.items()},
            "server": self.name
        }

class MCPClient(ABC):
    """
    Clase base para clientes MCP.
    Un cliente MCP puede solicitar recursos y ejecutar herramientas de servidores.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.connected_servers = {}  # Servidores a los que este cliente está conectado
    
    def connect_to_server(self, server_name: str, server: MCPServer):
        """Conecta este cliente a un servidor MCP"""
        self.connected_servers[server_name] = server
        logger.info(f"Cliente {self.name} conectado a servidor {server_name}")
    
    async def request_resource(self, server_name: str, resource_name: str) -> Any:
        """Solicita un recurso específico de un servidor"""
        if server_name not in self.connected_servers:
            raise ValueError(f"No conectado al servidor {server_name}")
        
        server = self.connected_servers[server_name]
        
        # Crear mensaje MCP para solicitar recurso
        message = MCPMessage(
            id=f"{self.name}_{resource_name}_{asyncio.get_event_loop().time()}",
            type=MCPMessageType.REQUEST,
            method="get_resource",
            params={"resource_name": resource_name}
        )
        
        response = await server.handle_request(message)
        
        if response.error:
            raise Exception(f"Error obteniendo recurso: {response.error}")
        
        return response.result
    
    async def execute_tool(self, server_name: str, tool_name: str, params: Dict[str, Any]) -> Any:
        """Ejecuta una herramienta en un servidor específico"""
        if server_name not in self.connected_servers:
            raise ValueError(f"No conectado al servidor {server_name}")
        
        server = self.connected_servers[server_name]
        
        # Crear mensaje MCP para ejecutar herramienta
        message = MCPMessage(
            id=f"{self.name}_{tool_name}_{asyncio.get_event_loop().time()}",
            type=MCPMessageType.REQUEST,
            method="execute_tool",
            params={"tool_name": tool_name, "tool_params": params}
        )
        
        response = await server.handle_request(message)
        
        if response.error:
            raise Exception(f"Error ejecutando herramienta: {response.error}")
        
        return response.result
    
    async def discover_servers(self) -> Dict[str, Dict[str, Any]]:
        """Descubre qué recursos y herramientas están disponibles en todos los servidores"""
        discovery = {}
        
        for server_name, server in self.connected_servers.items():
            try:
                resources = await server.get_resources()
                tools = await server.get_tools()
                discovery[server_name] = {
                    "resources": resources,
                    "tools": tools
                }
            except Exception as e:
                logger.error(f"Error descubriendo servidor {server_name}: {e}")
                discovery[server_name] = {"error": str(e)}
        
        return discovery

class MCPAgent(MCPServer, MCPClient):
    """
    Agente MCP que puede actuar tanto como servidor como cliente.
    Esta es la clase que usaremos para nuestros agentes de base de datos.
    """
    
    def __init__(self, name: str):
        MCPServer.__init__(self, name)
        MCPClient.__init__(self, name)
        logger.info(f"Agente MCP '{name}' creado")
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna el estado actual del agente"""
        return {
            "name": self.name,
            "initialized": self.initialized,
            "resources_count": len(self.resources),
            "tools_count": len(self.tools),
            "connected_servers": list(self.connected_servers.keys())
        }
    
# En mcp/base.py, agregar después de la definición de MCPAgent:
'''
class DatabaseAgent(MCPAgent):
    """
    Clase base especializada para agentes de base de datos.
    Hereda de MCPAgent y añade funcionalidad específica para bases de datos.
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.connection_params = {}
        
    async def connect(self):
        """Método abstracto para establecer conexión"""
        raise NotImplementedError("Subclases deben implementar connect()")
        
    async def disconnect(self):
        """Método abstracto para cerrar conexión"""
        raise NotImplementedError("Subclases deben implementar disconnect()")
        
    async def execute_query(self, query: str, params=None):
        """Método abstracto para ejecutar consultas"""
        raise NotImplementedError("Subclases deben implementar execute_query()")
'''

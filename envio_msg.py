import os
from dotenv import load_dotenv
from evolutionapi.client import EvolutionClient
from evolutionapi.models.message import TextMessage, MediaMessage

class SendMessage:
    
    def __init__(self) -> None:
        # Carregar variáveis de ambiente
        load_dotenv()
        self.evo_api_token = os.getenv("EVO_API_TOKEN")
        self.evo_instance_id = os.getenv("EVO_INSTANCE_ID")
        self.evo_instance_token = os.getenv("EVO_INSTANCE_TOKEN")
        self.evo_base_url = os.getenv("EVO_BASE_URL")
        
        # Inicializar o cliente Evolution
        self.client = EvolutionClient(
            base_url=self.evo_base_url,
            api_token=self.evo_api_token
        )

    def textMessage(self, number, msg, mentions=[]):
        # Enviar mensagem de texto
        text_message = TextMessage(
            number=str(number),
            text=msg,
            mentioned=mentions
        )

        response = self.client.messages.send_text(
            self.evo_instance_id, 
            text_message, 
            self.evo_instance_token
        )
        return response
